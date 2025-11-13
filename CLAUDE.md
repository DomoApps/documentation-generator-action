# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GitHub Action that generates professional Markdown documentation from YAML/OpenAPI specifications using AI. The action uses OpenAI's GPT models to intelligently populate documentation templates with content extracted from API specs.

**Key Insight:** The project uses a **hybrid approach** combining deterministic parsing with AI validation. The `process_openapi_to_markdown_deterministic` method parses the OpenAPI spec reliably, then validates output quality with AI and refines based on feedback. This gives us the reliability of deterministic parsing with the quality assurance of AI validation.

## Commands

### Local Development & Testing

```bash
# Set up environment (copy .env.example to .env and fill in API key)
export OPENAI_API_KEY="your-key"
export YAML_INPUT_PATH="./samples"
export MARKDOWN_OUTPUT_PATH="./output"
export TEMPLATE_PATH="./templates/product-api.template.md"

# Run the generator locally
python src/doc_generator_main.py

# Run unit tests (mocked, no API calls)
pytest

# Run integration tests (requires real OpenAI API key in .env)
pytest -m integration

# Run parser-only tests (no AI, deterministic parsing)
pytest tests/test_parser_only.py

# Run deterministic tests with AI
pytest tests/test_deterministic_with_ai.py
```

### GitHub Actions Testing

The action can be consumed as either:
1. **Composite Action**: `DomoApps/documentation-generator-action@main`
2. **Reusable Workflow**: `DomoApps/documentation-generator-action/.github/workflows/action.yml@main`

## Code Architecture

### Hybrid Processing Approach

**Primary Path (Hybrid: Deterministic + Validation)**:
1. `OpenAPIParser` (src/openapi/openapi_parser.py) parses the OpenAPI spec using prance for $ref resolution
2. Extracts all endpoints, parameters, schemas deterministically without AI
3. Generates examples from schemas using `ExampleGenerator`
4. AI fills the template with structured data
5. **AI validates** the generated documentation (completeness, accuracy, code quality, syntax)
6. **AI refines** based on validation feedback if quality threshold not met
7. **Iterates** up to max_iterations (default: 3) until quality threshold (default: 90%) achieved

**Fallback Path (Legacy Iterative)**:
1. AI analyzes YAML and extracts template data
2. AI generates markdown by populating template
3. AI validates quality and completeness
4. Iterative refinement loop until quality threshold met or max iterations reached

The hybrid approach is more reliable than legacy because the parsing is deterministic, but still gets the quality benefits of AI validation and refinement.

### Core Components

**Entry Point**: `src/doc_generator_main.py`
- Loads environment variables via `EnvVars` class
- Determines which YAML files to process (all or changed only)
- Calls `process_openapi_to_markdown_deterministic()` with fallback to legacy method
- Generates AI-powered PR titles when processing changed files
- Saves GENERATED_PR_TITLE to GITHUB_ENV for the GitHub Action

**AI Document Generator**: `src/ai/doc_generator.py` (extends `AiBot`)
- **Hybrid methods**:
  - `process_openapi_to_markdown_deterministic()`: Main entry point with validation loop
  - `_generate_endpoint_documentation()`: Fills template for one endpoint
  - `_build_parameter_table()`: Creates markdown tables from structured data
  - `_generate_nested_object_tables()`: Creates collapsible dropdowns for nested objects
  - `_combine_endpoint_docs()`: Assembles final document with TOC
- **Validation & refinement methods** (shared with legacy):
  - `_validate_documentation()`: Scores quality on 5 metrics (completeness, template_coverage, code_quality, markdown_syntax, overall)
  - `_refine_documentation()`: Targeted improvements based on validation feedback
  - `_should_exit()`: Checks if quality threshold met
- **Legacy iterative methods**: `process_yaml_to_markdown()`, `_analyze_yaml()`, `_generate_markdown()`
- **PR title generation**: `generate_pr_title()` - Creates AI-powered PR titles
- **JSON handling**: Multiple fallback strategies for extracting JSON from AI responses

**OpenAPI Parser**: `src/openapi/openapi_parser.py`
- Uses prance library for $ref resolution (with manual fallback for circular refs)
- `parse_all_endpoints()`: Returns list of `EndpointData` objects
- `_resolve_ref()`: Manual $ref resolution with recursion protection
- Handles _Nullable schema patterns (common in real-world specs)
- Pre-processes specs to fix common validation issues (e.g., empty server objects)

**Example Generator**: `src/openapi/example_generator.py`
- Generates realistic examples from OpenAPI schemas
- Extracts existing examples from specs when available
- Type-aware generation (strings, numbers, booleans, arrays, objects)

**Environment Variables**: `src/env_vars.py`
- Loads `.env` file for local development
- Validates required environment variables
- Provides defaults for optional parameters

### Data Flow

**Hybrid Approach (Primary)**:
```
YAML File → OpenAPIParser → List[EndpointData] → DocGenerator → AI (template filling) → Markdown
                ↓                                                           ↓
         ExampleGenerator                                          AI Validation
                                                                         ↓
                                                              Quality Check (90% threshold)
                                                                         ↓
                                                            ┌───── Pass → Done
                                                            └───── Fail → AI Refinement → Loop
```

**Legacy Iterative Approach (Fallback)**:
```
YAML → AI Analysis → Template Data → AI Generation → Markdown → AI Validation → Refinement Loop
```

### Key Data Structures

**EndpointData** (src/openapi/openapi_parser.py):
- Contains all structured data for a single API endpoint
- Properties: path, method, operation_id, summary, description, tags
- Parameters: path_parameters, query_parameters, header_parameters
- Request body: request_body_schema, request_body_parameters, request_body_example
- Responses: responses dict, success_response_example, success_status_code

### Template System

Templates use Handlebars-style placeholders:
- Simple: `{{API_NAME}}`, `{{HTTP_METHOD}}`, `{{ENDPOINT_PATH}}`
- Tables: `{{PATH_PARAMETERS_TABLE}}`, `{{REQUEST_BODY_TABLE}}`
- Examples: `{{REQUEST_BODY_EXAMPLE}}`, `{{RESPONSE_EXAMPLE}}`
- Special: `{{NESTED_OBJECT_TABLES}}` - Collapsible dropdowns for nested schemas

The deterministic approach builds these tables directly in Python, then AI fills the complete template.

### GitHub Actions Integration

**Change Detection** (action.yml lines 87-131):
- Determines base reference (PR base, previous commit on main, or origin/main)
- Uses `git diff` to find changed YAML files
- Sets `has_changes` output to skip processing if no YAML files changed

**PR Creation** (action.yml lines 198-232):
- Uses peter-evans/create-pull-request@v5
- PR title comes from `GENERATED_PR_TITLE` env var (AI-generated) or falls back to `pr_title` input
- Auto-assigns PR to the actor who triggered the workflow
- Branch name includes timestamp suffix to avoid conflicts

## Testing Strategy

**Unit Tests**: Mock OpenAI API, focus on logic
**Integration Tests**: Use `@pytest.mark.integration`, require real API key
**Parser Tests**: Test deterministic parsing without AI
**Deterministic Tests**: Test full deterministic flow with AI

Test fixtures in `tests/conftest.py` auto-load `.env` file and mock environment variables for unit tests.

## Validation & Quality Control

The hybrid approach validates documentation on 5 key metrics (0-100 scale):

1. **Completeness**: Are all YAML/OpenAPI elements documented?
2. **Template Coverage**: Are all template placeholders filled?
3. **Code Quality**: Are code examples realistic and functional?
4. **Markdown Syntax**: Is the markdown properly formatted?
5. **Overall**: Aggregate score that determines if refinement is needed

**Exit Conditions**:
- Overall score ≥ completeness_threshold (default: 90%)
- AND exit_criteria_met flag is true
- OR max_iterations reached (default: 3 for hybrid, 10 for legacy)

**Refinement Strategy**:
The AI receives specific feedback about what's missing or incorrect, then makes targeted improvements rather than regenerating from scratch. This preserves the deterministic structure while fixing specific issues.

## Common Patterns & Gotchas

1. **JSON Extraction**: AI responses often contain markdown code blocks or extra text. The `_extract_json_from_response()` method has 4 fallback strategies to handle this.

2. **Circular $refs**: OpenAPI specs can have circular references. The parser uses manual $ref resolution with max depth protection instead of relying solely on prance.

3. **_Nullable Schemas**: Many real-world OpenAPI specs use `_Nullable` suffixed schemas for optional complex types. The parser detects and resolves these to their base schemas.

4. **Nested Object Documentation**: Complex request bodies with nested objects are documented using collapsible markdown dropdowns (`<details>` tags) to avoid overwhelming the reader.

5. **Schema-level Descriptions**: Request body schemas often have important descriptions at the schema level (not just property level). These are captured in `request_body_description` and included in documentation.

6. **Fallback Mechanisms**: Every AI call and parsing operation has fallback logic to ensure the action doesn't fail completely. Check for Log.print_red() warnings when debugging.

## Repository Structure Notes

- `samples/`: Contains example YAML files for testing (e.g., filesets.yaml)
- `templates/`: Default template is `product-api.template.md`
- `output/`: Generated markdown files (gitignored)
- `tests/`: Comprehensive test suite with integration and unit tests
- `.env`: Local development environment variables (gitignored, use .env.example as template)

## Development Workflow

When adding new features:
1. Add tests first (TDD approach preferred)
2. Implement in deterministic path if possible (better reliability)
3. Update CONTEXT.md if architecture changes significantly
4. Test locally with real OpenAPI specs from `samples/`
5. Run both unit and integration tests before committing
6. Update action.yml if adding new inputs/outputs
