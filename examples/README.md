# Examples

This directory contains example workflows demonstrating common usage patterns for the OpenAPI TOC Generator.

## Workflow Examples

### [basic-usage.yml](./basic-usage.yml)
The simplest setup - processes all YAML files on every push and commits the updated `docs.json` directly.

### [with-change-detection.yml](./with-change-detection.yml)
Only processes YAML files that have changed, reducing unnecessary processing. Requires `fetch-depth: 0` for git history access.

### [with-pull-request.yml](./with-pull-request.yml)
Creates a pull request with the updated navigation instead of committing directly. Useful for review workflows.

### [copy-yaml-files.yml](./copy-yaml-files.yml)
Copies YAML files to a destination directory (e.g., your Mintlify docs folder) in addition to updating `docs.json`.

## Directory Structure

A typical Mintlify docs repository using this action:

```
your-docs-repo/
├── docs.json                 # Mintlify configuration (updated by action)
├── openapi/
│   └── product/              # OpenAPI specs copied here
│       ├── users.yaml
│       └── documents.yaml
├── yaml/                     # Source YAML files (input)
│   ├── users.yaml
│   └── documents.yaml
└── .github/
    └── workflows/
        └── update-api-nav.yml
```

## Configuration Reference

| Input | Description | Default |
|-------|-------------|---------|
| `yaml_input_path` | Source directory for OpenAPI YAML files | `./yaml` |
| `docs_json_path` | Path to Mintlify docs.json | **Required** |
| `openapi_base_path` | Prefix for page references in docs.json | `openapi/product` |
| `yaml_copy_destination` | Copy YAMLs here after processing | - |
| `process_changed_only` | Only process changed files | `false` |
| `create_pull_request` | Create PR instead of direct commit | `false` |

## Cross-Repo Sync

For syncing OpenAPI specs from a separate source repository, see [destination-repo/](./destination-repo/).

This includes:
- **Scripts** for detecting changes and syncing files across repos
- **Workflows** for both direct commit and PR-based approaches
- Support for GitHub App authentication

```
destination-repo/
└── .github/
    ├── scripts/
    │   ├── detect_yaml_changes.py   # Detect changed files
    │   ├── sync_to_destination.py   # Copy files to destination
    │   └── create_individual_prs.py # Create PRs per file
    └── workflows/
        ├── sync-api-docs.yml        # Direct commit workflow
        └── sync-with-prs.yml        # Individual PR workflow
```
