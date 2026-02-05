# OpenAPI TOC Generator for Mintlify

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A GitHub Action that generates Mintlify-compatible Table of Contents (TOC) entries from OpenAPI YAML specifications. Automatically updates your `docs.json` navigation with structured API endpoint references.

## Features

- **Deterministic Processing**: No AI involved - consistent, reproducible output every time
- **Mintlify Integration**: Generates navigation entries compatible with Mintlify's OpenAPI support
- **Tag-Based Grouping**: Endpoints automatically organized by OpenAPI tags
- **Method Sorting**: Endpoints sorted alphabetically by HTTP method (DELETE, GET, PATCH, POST, PUT)
- **Change Detection**: Only process modified YAML files for efficient CI/CD
- **Automatic PR Creation**: Optionally create pull requests with updated navigation

## Quick Start

```yaml
name: Update API Navigation

on:
  push:
    paths:
      - 'yaml/**/*.yaml'
      - 'yaml/**/*.yml'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate API Navigation
        uses: DomoApps/documentation-generator-action@main
        with:
          yaml_input_path: './yaml'
          docs_json_path: './docs.json'
          openapi_base_path: 'openapi/product'
```

See the [examples](./examples/) directory for more workflow patterns including change detection, PR creation, and YAML file copying.

## Configuration

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `yaml_input_path` | Directory containing OpenAPI YAML files | `./yaml` | No |
| `docs_json_path` | Path to Mintlify docs.json file | - | **Yes** |
| `openapi_base_path` | Base path for OpenAPI references in docs.json | `openapi/product` | No |
| `yaml_copy_destination` | Copy YAML files to this directory after processing | - | No |
| `process_changed_only` | Only process changed YAML files | `false` | No |
| `changed_files` | Newline-separated list of files to process | - | No |
| `base_ref` | Base reference for change detection | `main` | No |
| `create_pull_request` | Create PR with updated docs.json | `false` | No |
| `pr_title` | Title for the pull request | `Update API navigation in docs.json` | No |
| `pr_branch_name` | Branch name for the PR | `docs/update-api-navigation` | No |

## Output Format

For each OpenAPI specification, the action generates navigation entries:

```json
{
  "group": "Documents API",
  "pages": [
    {
      "group": "Documents",
      "pages": [
        "openapi/product/documents.yaml DELETE /documents/{id}",
        "openapi/product/documents.yaml GET /documents",
        "openapi/product/documents.yaml GET /documents/{id}",
        "openapi/product/documents.yaml POST /documents"
      ]
    }
  ]
}
```

**Format details:**
- Group name comes from `info.title` in the OpenAPI spec
- Nested groups are based on OpenAPI tags
- Page format: `{openapi_base_path}/{filename}.yaml {METHOD} {path}`
- Endpoints without tags are grouped under "Untagged"

## Change Detection

Enable efficient processing by only regenerating docs for changed files:

```yaml
- uses: DomoApps/documentation-generator-action@main
  with:
    yaml_input_path: './yaml'
    docs_json_path: './docs.json'
    process_changed_only: 'true'
```

**Requirements:**
- Set `fetch-depth: 0` in checkout action for git history access
- Works with push events, pull requests, and manual triggers

## Local Development

```bash
# Set environment variables
export YAML_INPUT_PATH="./samples"
export DOCS_JSON_PATH="./path/to/docs.json"
export OPENAPI_BASE_PATH="openapi/product"

# Run the generator
python src/toc_generator_main.py

# Run tests
pytest
```

## Outputs

| Output | Description |
|--------|-------------|
| `files_processed` | Number of YAML files processed |
| `groups_updated` | Number of API groups updated in docs.json |

## Contributing

1. Create a branch `<your-name>/<feature-or-fix>` from `main`
2. Make changes and write tests
3. Run `pytest` to verify
4. Submit a pull request

## License

Apache 2.0
