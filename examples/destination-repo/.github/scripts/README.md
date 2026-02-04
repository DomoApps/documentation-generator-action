# Destination Repo Scripts

These scripts are designed to be copied to your destination repository (e.g., `DomoApps/domo-developer-portal`) to handle cross-repo YAML enhancement synchronization.

## Overview

These scripts work together to:
1. Detect which YAML files in the source repo have changed
2. Enhance them with AI-generated descriptions
3. Sync the enhanced YAML files to the destination repo
4. Create individual PRs for review

## Scripts

### 1. `detect_yaml_changes.py`

**Purpose:** Detects which YAML files in the source repo have changed compared to their corresponding YAML files in the destination repo.

**How it works:**
- Compares modification timestamps between source and destination YAML files
- Files have the same name in both source and destination
- Outputs a list of files that need enhancement

**Usage:**
```bash
python detect_yaml_changes.py \
  --source source-repo/api-docs/public \
  --dest docs/API-Reference/Product-APIs \
  --force false
```

**Arguments:**
- `--source`: Path to source repo YAML directory
- `--dest`: Path to destination repo YAML directory
- `--force`: Set to `true` to force re-enhancement of all files

**Output:**
- Creates `changed_files.txt` with list of YAML files to process
- Outputs summary to GitHub Actions output

---

### 2. `sync_to_destination.py`

**Purpose:** Copies enhanced YAML files from temp directory to destination, preserving filenames.

**How it works:**
- Reads list of changed YAML files
- Copies enhanced YAML files from temp directory to destination
- Files maintain the same name (no mapping needed)
- Preserves YAML structure, comments, and formatting

**Usage:**
```bash
python sync_to_destination.py \
  --source source-repo/api-docs/public \
  --enhanced ./temp-enhanced-yaml \
  --destination docs/API-Reference/Product-APIs \
  --changed-list changed_files.txt
```

**Arguments:**
- `--source`: Source YAML directory (for reference)
- `--enhanced`: Directory with enhanced YAML files (temp location)
- `--destination`: Destination directory for YAML files
- `--changed-list`: File containing list of changed YAML files to sync

**Output:**
- Copies enhanced YAML files to destination
- Prints summary of synced files

---

### 3. `create_individual_prs.py`

**Purpose:** Creates individual pull requests for each enhanced YAML file with duplicate prevention.

**How it works:**
- Reads list of changed YAML files
- For each file:
  - Checks if an open PR already exists (skip if so)
  - Creates a new git branch
  - Copies enhanced YAML to destination (same filename)
  - Commits changes
  - Creates a PR with detailed description
- Handles all git operations, error recovery, and branch management

**Usage:**
```bash
python create_individual_prs.py \
  --changed-list changed_files.txt \
  --temp-dir ./temp-enhanced-yaml \
  --dest-dir docs/API-Reference/Product-APIs \
  --base-branch master \
  --pr-branch-prefix yaml-enhance \
  --openai-model gpt-4o \
  --max-iterations 3 \
  --quality-threshold 85 \
  --repo DomoApps/domo-developer-portal
```

**Arguments:**
- `--changed-list`: File containing list of changed YAML files
- `--temp-dir`: Directory with enhanced YAML files
- `--dest-dir`: Destination directory for YAML files
- `--base-branch`: Base branch to create PRs from (default: master)
- `--pr-branch-prefix`: Branch name prefix for PRs (default: yaml-enhance)
- `--openai-model`: AI model used (for PR description)
- `--max-iterations`: Max iterations used (for PR description)
- `--quality-threshold`: Quality threshold used (for PR description)
- `--repo`: GitHub repository in owner/repo format (optional)

**Output:**
- Creates individual PRs for each file
- Returns exit code 1 if any PRs failed to create
- Prints summary of processed/skipped/failed files

**Features:**
- ✅ Duplicate PR prevention (checks for existing open PRs)
- ✅ Comprehensive error handling and recovery
- ✅ Detailed logging for debugging
- ✅ Git branch management (create/checkout/cleanup)
- ✅ Simple 1:1 file syncing (no mapping needed)
- ✅ Preserves YAML structure and comments

---

## Script Dependencies

All scripts require:
- Python 3.7+
- Standard library only (no external dependencies for detect/sync scripts)
- `create_individual_prs.py` requires:
  - `git` CLI
  - `gh` (GitHub CLI)
  - Proper authentication (via GH_TOKEN environment variable)

## Workflow Integration

These scripts are designed to work together in the following order:

1. **detect_yaml_changes.py** - Identifies files that need updates
2. **YAML Enhancement** - Action enhances YAML files with AI-generated descriptions
3. **create_individual_prs.py** - Creates PRs for enhanced YAML files

See `examples/destination-repo/workflows/sync-api-docs.yml` for complete workflow example.

## File Naming Convention

**Simple 1:1 mapping** - No configuration file needed!

- Source: `source-repo/api-docs/public/ai.yaml`
- Destination: `docs/API-Reference/Product-APIs/ai.yaml`
- Files keep the same name, just different directories

## Testing Scripts Locally

```bash
# Test detection
python .github/scripts/detect_yaml_changes.py \
  --source ../source-repo/api-docs/public \
  --dest docs/API-Reference/Product-APIs

# Test sync
python .github/scripts/sync_to_destination.py \
  --source ../source-repo/api-docs/public \
  --enhanced ./temp-enhanced-yaml \
  --destination docs/API-Reference/Product-APIs \
  --changed-list changed_files.txt

# Test PR creation (requires git repo and gh CLI)
export GH_TOKEN="your_token"
python .github/scripts/create_individual_prs.py \
  --changed-list changed_files.txt \
  --temp-dir ./temp-enhanced-yaml \
  --dest-dir docs/API-Reference/Product-APIs \
  --base-branch master \
  --repo your-org/your-repo
```

## What Gets Enhanced

The AI enhancement process adds contextual descriptions to:

- ✅ **info.title** - API title
- ✅ **info.description** - Overall API description
- ✅ **tags** - Tag descriptions for endpoint grouping
- ✅ **endpoints** - Endpoint descriptions (operation summaries)
- ✅ **parameters** - Path, query, header parameter descriptions
- ✅ **schemas** - Component schema descriptions
- ✅ **properties** - Schema property descriptions

All enhancements:
- Preserve original YAML structure
- Maintain comments and formatting
- Use contextual AI to generate meaningful descriptions
- Undergo quality validation (default: 85% threshold)

## Troubleshooting

### Script fails with "command not found"
- Ensure Python 3.7+ is installed: `python --version`
- For `create_individual_prs.py`, ensure `git` and `gh` CLI are installed

### "No changes detected" but files have changed
- Check file modification timestamps
- Verify source and destination paths are correct
- Use `--force true` flag with detect_yaml_changes.py

### PR creation fails with authentication error
- Ensure `GH_TOKEN` environment variable is set
- Verify token has required permissions (repo, pull_requests)
- Check GitHub App configuration if using app authentication

### Enhanced YAML appears corrupted
- Check ruamel.yaml is installed in the action environment
- Verify original YAML was valid OpenAPI spec
- Review enhancement logs for parsing errors
