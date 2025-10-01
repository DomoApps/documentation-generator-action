# AI Bot Context Memory

## Project Overview
**Name:** YAML to Markdown Documentation Generator (GitHub Action)
**Organization:** DomoApps
**Repository:** documentation-generator-action
**License:** Apache 2.0
**Author:** Jonathan Tiritilli

## Purpose
AI-powered GitHub Action that automatically generates professional Markdown documentation from YAML files. Primarily used for API documentation with iterative refinement and quality control.

## Core Architecture

### Main Components
1. **doc_generator.py** (`src/ai/doc_generator.py`)
   - Main AI bot implementation extending `AiBot` base class
   - Uses OpenAI API (default model: `gpt-4o`)
   - Iterative refinement loop with quality scoring
   - JSON extraction and validation logic
   - PR title generation functionality

2. **doc_generator_main.py** (`src/doc_generator_main.py`)
   - Entry point for the action
   - Handles environment variables
   - Processes YAML files (batch or changed-only)
   - Manages file I/O operations

3. **GitHub Actions**
   - `action.yml`: Composite action definition
   - `.github/workflows/action.yml`: Reusable workflow
   - `workflow-example.yml`: Usage example

### Key Features
- 🤖 **AI-Powered Generation** - OpenAI GPT models for intelligent content
- 📄 **Template-Based** - Handlebars-style templates
- 🔄 **Iterative Refinement** - Multi-pass generation (default: 10 iterations)
- 📊 **Quality Control** - 90% completeness threshold default
- 🎯 **Smart Change Detection** - Only process changed YAML files
- 🔀 **Auto PR Creation** - Built-in pull request generation
- 🧠 **Smart PR Titles** - AI-generated descriptive titles

## Processing Flow

```
1. YAML Analysis → Extract data and structure
2. Template Population → Map YAML to template placeholders
3. Markdown Generation → Create initial documentation
4. Quality Validation → Score completeness, coverage, code quality, syntax
5. Refinement Loop → Improve until threshold met or max iterations
```

### Exit Conditions
- Overall quality score ≥ 90% (configurable)
- All template placeholders filled
- No critical documentation gaps
- Maximum iterations reached (default: 10)

## Configuration Options

| Input | Default | Purpose |
|-------|---------|---------|
| `openai_api_key` | (required) | OpenAI authentication |
| `yaml_input_path` | `./yaml` | YAML source directory |
| `output_path` | `./docs` | Documentation output directory |
| `template_path` | `default` | Custom template file |
| `openai_model` | `gpt-4o` | AI model selection |
| `max_iterations` | `10` | Refinement iteration limit |
| `completeness_threshold` | `90` | Quality score threshold (0-100) |
| `process_changed_only` | `false` | Change detection mode |
| `create_pull_request` | `false` | Auto-create PR |
| `pr_title` | `📚 Update API Documentation` | Fallback PR title |

## AI Bot Implementation Details

### DocGenerator Class Methods

**Main Processing:**
- `process_yaml_to_markdown()` - Main iteration loop
- `_analyze_yaml()` - Extract template data from YAML
- `_generate_markdown()` - Populate template with data
- `_validate_documentation()` - Score quality and completeness
- `_refine_documentation()` - Improve based on feedback
- `_should_exit()` - Check exit conditions

**JSON Handling:**
- `_extract_json_from_response()` - Extract JSON from AI response
- `_extract_balanced_json()` - Balanced bracket counting parser
- `_clean_json_response()` - Fix common JSON issues
- `_is_valid_json()` - Validation check
- `_create_fallback_analysis()` - Fallback structure

**PR Features:**
- `generate_pr_title()` - AI-generated PR titles (60 char max)
- `_create_changes_summary()` - Summarize file changes
- `_create_fallback_pr_title()` - Fallback title generation

**Utility:**
- `_extract_template_placeholders()` - Regex extraction of `{{placeholders}}`
- `_make_ai_request()` - OpenAI API wrapper

## Template System

Uses Handlebars-style syntax:
- `{{API_NAME}}` - Simple placeholders
- `{{#each PARAMETERS}}...{{/each}}` - Loops
- `{{#if CONDITION}}...{{/if}}` - Conditionals

Example placeholders:
- `{{API_NAME}}`, `{{API_DESCRIPTION}}`
- `{{ENDPOINT_PATH}}`, `{{HTTP_METHOD}}`
- `{{PARAMETERS}}`, `{{RESPONSES}}`

## Recent Changes (from git commits)

1. **JSON Import Fix** - Added missing `json` import
2. **Environment Variables** - `GENERATED_PR_TITLE` support
3. **Smart PR Titles** - AI-generated titles based on changes
4. **Change Detection** - Compare against previous commit in push events
5. **Path Handling** - Remove leading `./` from input paths

## Project Structure

```
/
├── src/
│   ├── ai/
│   │   ├── ai_bot.py          # Base class
│   │   ├── doc_generator.py   # Main AI bot
│   │   └── __init__.py
│   ├── doc_generator_main.py  # Entry point
│   ├── env_vars.py            # Environment handling
│   └── log.py                 # Logging utilities
├── tests/
│   ├── test_doc_generator.py
│   └── conftest.py
├── samples/
│   ├── filesets.yaml          # Example API spec
│   └── productAPI.template.md # Example template
├── action.yml                 # Composite action
├── workflow-example.yml       # Usage example
└── README.md                  # Documentation
```

## Technology Stack
- **Language:** Python 3.x
- **AI Provider:** OpenAI (GPT models)
- **Platform:** GitHub Actions
- **Testing:** pytest
- **Dependencies:** openai, yaml

## Usage Patterns

### Basic Usage
```yaml
- uses: DomoApps/documentation-generator-action@main
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    yaml_input_path: "./yaml"
    output_path: "./docs"
```

### With Smart Features
```yaml
- uses: DomoApps/documentation-generator-action@main
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    yaml_input_path: "./yaml"
    output_path: "./docs"
    process_changed_only: "true"    # Only changed files
    create_pull_request: "true"     # Auto-create PR
```

## Important Notes

- **Case Sensitive:** Use exact case `DomoApps/documentation-generator-action`
- **Fetch Depth:** Requires `fetch-depth: 0` for change detection
- **Permissions:** Needs `contents: write` and `pull-requests: write`
- **API Costs:** OpenAI API calls are made per file per iteration

## Testing

Local testing:
```bash
export OPENAI_API_KEY="your-key"
export YAML_INPUT_PATH="./samples"
export MARKDOWN_OUTPUT_PATH="./output"
python src/doc_generator_main.py
```

## Quality Metrics

The validation scoring system evaluates:
1. **Completeness** (0-100) - All YAML elements documented
2. **Template Coverage** (0-100) - All placeholders filled
3. **Code Quality** (0-100) - Realistic, functional examples
4. **Markdown Syntax** (0-100) - Valid formatting
5. **Overall** (0-100) - Aggregate score

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| JSON parsing errors | Multiple fallback strategies in place |
| API rate limits | Adjust `max_iterations` or use caching |
| Missing placeholders | Check template compatibility |
| Change detection issues | Ensure `fetch-depth: 0` in checkout |

## Future Considerations
- Support for additional AI providers
- Template validation before processing
- Caching mechanism for repeated runs
- Support for other documentation formats
