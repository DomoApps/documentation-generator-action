# Destination Repo Scripts

These scripts are designed to be copied to your destination repository (e.g., your Mintlify docs repo) to handle cross-repo OpenAPI synchronization.

## Overview

These scripts work together to:
1. Detect which YAML files in the source repo have changed
2. Sync the YAML files to the destination repo
3. Create PRs for review (optional)

The TOC generator action then updates `docs.json` navigation automatically.

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

---

### `create_individual_prs.py`

Creates individual pull requests for each changed YAML file. Includes duplicate PR prevention.

```bash
python create_individual_prs.py \
  --changed-list changed_files.txt \
  --source-dir source-repo/api-specs \
  --dest-dir openapi/product \
  --base-branch main \
  --pr-branch-prefix openapi-sync \
  --repo your-org/your-repo
```

**Arguments:**
- `--changed-list`: File containing list of changed YAML files
- `--source-dir`: Source directory with YAML files
- `--dest-dir`: Destination directory for YAML files
- `--base-branch`: Base branch for PRs (default: main)
- `--pr-branch-prefix`: Branch name prefix (default: openapi-sync)
- `--repo`: GitHub repository in owner/repo format

**Features:**
- Duplicate PR prevention (skips files with existing open PRs)
- Comprehensive error handling
- Git branch management

## Workflow Integration

### Direct Commit Workflow

Use `sync-api-docs.yml` for automatic sync without PRs:

1. Detect changes
2. Sync YAML files
3. Run TOC generator to update docs.json
4. Commit directly to main

### PR-Based Workflow

Use `sync-with-prs.yml` + `update-navigation-on-merge.yml` when you want review:

1. `sync-with-prs.yml`: Detect changes → Create individual PR for each file
2. Review and merge PRs
3. `update-navigation-on-merge.yml`: Triggers on merge → Updates docs.json

## Requirements

- Python 3.7+
- `git` CLI
- `gh` (GitHub CLI) - for PR creation
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
    │   ├── sync_to_destination.py
    │   └── create_individual_prs.py
    └── workflows/
        ├── sync-api-docs.yml              # Direct commit (all-in-one)
        ├── sync-with-prs.yml              # Create individual PRs
        └── update-navigation-on-merge.yml # Update docs.json on merge
```
