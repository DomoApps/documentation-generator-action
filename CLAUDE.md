# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GitHub Action that generates Mintlify-compatible Table of Contents (TOC) JSON from OpenAPI YAML specifications. The action deterministically parses OpenAPI specs and generates navigation entries for Mintlify `docs.json`.

**Key Insight:** This project uses a **fully deterministic approach** - no AI is involved. The `TOCGenerator` parses OpenAPI specs using prance and generates structured TOC entries based on API tags and endpoints.

## Commands

### Local Development & Testing

```bash
# Set up environment variables
export YAML_INPUT_PATH="./samples"
export DOCS_JSON_PATH="./path/to/docs.json"
export OPENAPI_BASE_PATH="openapi/product"

# Run the generator locally
python src/toc_generator_main.py

# Run all tests
pytest

# Run parser-only tests (deterministic parsing)
pytest tests/test_parser_only.py

# Run TOC generator tests
pytest tests/test_toc_generator.py
```

### GitHub Actions Usage

```yaml
- uses: DomoApps/documentation-generator-action@main
  with:
    yaml_input_path: './yaml'
    docs_json_path: './docs.json'
    openapi_base_path: 'openapi/product'
```

## Code Architecture

### Processing Flow

```
YAML Files → OpenAPIParser → EndpointData → TOCGenerator → TOC JSON → DocsJsonManager → docs.json
```

### Core Components

**Entry Point**: `src/toc_generator_main.py`
- Loads environment variables via `EnvVars` class
- Determines which YAML files to process (all or changed only)
- Calls `TOCGenerator` to generate TOC entries
- Uses `DocsJsonManager` to update docs.json
- Optionally copies YAML files to destination

**TOC Generator**: `src/toc_generator.py`
- `generate_toc_for_file()`: Generates TOC for a single YAML file
- `generate_toc_for_directory()`: Processes all YAML files in a directory
- `_group_endpoints_by_tag()`: Groups endpoints by their first tag
- `_sort_endpoints_by_method()`: Alphabetically sorts endpoints by HTTP method
- `_format_page_string()`: Formats Mintlify page references

**Docs JSON Manager**: `src/docs_json_manager.py`
- `load()` / `save()`: Read and write docs.json
- `find_api_reference_pages()`: Navigate to API Reference tab pages
- `insert_or_replace_group()`: Insert or update TOC group
- `remove_group()`: Remove a TOC group
- `get_existing_groups()`: List current groups

**OpenAPI Parser**: `src/openapi/openapi_parser.py`
- Uses prance library for $ref resolution (with manual fallback for circular refs)
- `parse_all_endpoints()`: Returns list of `EndpointData` objects
- `get_api_info()`: Returns API title, description, version, tags
- Handles _Nullable schema patterns (common in real-world specs)
- Pre-processes specs to fix common validation issues

**Environment Variables**: `src/env_vars.py`
- `DOCS_JSON_PATH` (required): Path to docs.json to update
- `YAML_INPUT_PATH` (default: ./yaml): Source YAML directory
- `OPENAPI_BASE_PATH` (default: openapi/product): Prefix for page paths
- `YAML_COPY_DESTINATION` (optional): Copy YAMLs to this directory
- `PROCESS_CHANGED_ONLY` (default: false): Only process changed files
- `CHANGED_FILES`: Newline-separated list of changed files

### Output Format

For each YAML file, generates:
```json
{
  "group": "API Title from YAML",
  "pages": [
    {
      "group": "Tag Name",
      "pages": [
        "openapi/product/filename.yaml DELETE /path",
        "openapi/product/filename.yaml GET /path",
        "openapi/product/filename.yaml POST /path"
      ]
    }
  ]
}
```

**Key Format Rules**:
- Group name comes from `info.title` in YAML
- Nested groups are based on OpenAPI tags
- Page format: `{openapi_base_path}/{filename}.yaml {METHOD} {path}`
- Methods are sorted alphabetically (DELETE, GET, PATCH, POST, PUT)

### Key Data Structures

**EndpointData** (src/openapi/openapi_parser.py):
- Contains all structured data for a single API endpoint
- Properties: path, method, operation_id, summary, description, tags
- Parameters: path_parameters, query_parameters, header_parameters
- Request body: request_body_schema, request_body_parameters, request_body_example
- Responses: responses dict, success_response_example, success_status_code

### GitHub Actions Integration

**Change Detection** (action.yml):
- Determines base reference (PR base, previous commit on main, or origin/main)
- Uses `git diff` to find changed YAML files
- Sets `has_changes` output to skip processing if no YAML files changed

**PR Creation**:
- Uses peter-evans/create-pull-request@v5
- Auto-assigns PR to the actor who triggered the workflow
- Branch name includes timestamp suffix to avoid conflicts

## Testing Strategy

**Unit Tests**: Test TOCGenerator and DocsJsonManager logic
**Parser Tests**: Test deterministic parsing without external dependencies
**Integration Tests**: Full workflow tests with sample YAML files

Test fixtures in `tests/conftest.py` auto-load `.env` file.

## Common Patterns & Gotchas

1. **Circular $refs**: OpenAPI specs can have circular references. The parser uses manual $ref resolution with max depth protection instead of relying solely on prance.

2. **_Nullable Schemas**: Many real-world OpenAPI specs use `_Nullable` suffixed schemas for optional complex types. The parser detects and resolves these to their base schemas.

3. **Untagged Endpoints**: Endpoints without tags are grouped under "Untagged" in the TOC.

4. **Empty Server Objects**: Invalid specs with empty server objects are pre-processed and fixed before parsing.

5. **Debugging**: Check for `Log.print_red()` warnings when debugging failures.

## Repository Structure

- `src/toc_generator.py`: Core TOC generation logic
- `src/docs_json_manager.py`: docs.json manipulation
- `src/toc_generator_main.py`: Entry point
- `src/env_vars.py`: Environment variable handling
- `src/openapi/openapi_parser.py`: OpenAPI parsing
- `src/openapi/example_generator.py`: Example generation (kept for parser)
- `src/log.py`: Logging utility
- `samples/`: Example YAML files for testing
- `tests/`: Test suite

## Development Workflow

When adding new features:
1. Add tests first (TDD approach preferred)
2. Test locally with real OpenAPI specs from `samples/`
3. Run all tests before committing
4. Update action.yml if adding new inputs/outputs
