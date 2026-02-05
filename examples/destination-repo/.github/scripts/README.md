# Destination Repo Scripts

These scripts are designed to be copied to your destination repository (e.g., your Mintlify docs repo) to handle cross-repo OpenAPI synchronization.

## Overview

These scripts work together to:
1. Detect which YAML files in the source repo have changed
2. Sync the YAML files to the destination repo
3. Update docs.json navigation with the TOC generator
4. Create a single PR with all changes for review

## Scripts

### `detect_yaml_changes.py`

Detects which YAML files in the source repo have changed compared to the destination.

```bash
python detect_yaml_changes.py \
  --source source-repo/api-specs \
  --dest openapi/product \
  --force false
```

**Arguments:**
- `--source`: Path to source repo YAML directory
- `--dest`: Path to destination repo YAML directory
- `--force`: Set to `true` to force sync all files

**Output:**
- Creates `changed_files.txt` with list of files to sync
- Sets GitHub Actions outputs: `changed_files`, `summary`

---

### `sync_to_destination.py`

Copies YAML files from source to destination directory.

```bash
python sync_to_destination.py \
  --source source-repo/api-specs \
  --destination openapi/product \
  --changed-list changed_files.txt
```

**Arguments:**
- `--source`: Source YAML directory
- `--destination`: Destination directory for YAML files
- `--changed-list`: File containing list of files to sync

## Workflow

Use `sync-api-docs.yml` for the complete sync workflow:

1. Detect changes in source repo
2. Sync YAML files to destination
3. Run TOC generator to update docs.json
4. Create a single PR with all changes (YAMLs + navigation)

### Benefits

- **Complete visibility**: Reviewers see both YAML and navigation changes in one PR
- **Testable**: Navigation can be previewed before merge (if using Mintlify preview)
- **No conflicts**: Single PR avoids merge conflicts on docs.json
- **Simple**: One workflow instead of multiple

## Requirements

- Python 3.7+
- `git` CLI
- GitHub App or PAT for cross-repo access

## File Structure

```
destination-repo/
├── docs.json                    # Updated by TOC generator
├── openapi/
│   └── product/                 # YAML files synced here
│       ├── users.yaml
│       └── documents.yaml
└── .github/
    ├── scripts/
    │   ├── detect_yaml_changes.py
    │   └── sync_to_destination.py
    └── workflows/
        └── sync-api-docs.yml    # Single workflow for sync + PR
```
