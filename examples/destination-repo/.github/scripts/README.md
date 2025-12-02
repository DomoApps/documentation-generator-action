# Destination Repo Scripts

These scripts are designed to be copied to your destination repository (e.g., `DomoApps/domo-developer-portal`) to handle cross-repo documentation synchronization.

## Scripts

### 1. `detect_yaml_changes.py`

**Purpose:** Detects which YAML files in the source repo have changed compared to their corresponding markdown files in the destination repo.

**How it works:**
- Compares modification timestamps between source YAML and destination markdown files
- Uses the mapping configuration to determine which files to compare
- Outputs a list of files that need regeneration

**Usage:**
```bash
python detect_yaml_changes.py \
  --source source-repo/api-docs/public \
  --dest docs/API-Reference/Product-APIs \
  --mapping .github/doc-mapping.json \
  --force false
```

**Arguments:**
- `--source`: Path to source repo YAML directory
- `--dest`: Path to destination repo markdown directory
- `--mapping`: Path to mapping configuration file
- `--force`: Set to `true` to force regeneration of all files

**Output:**
- Creates `changed_files.txt` with list of YAML files to process

---

### 2. `sync_to_destination.py`

**Purpose:** Maps generated markdown files from temp directory to their proper destination paths based on mapping configuration.

**How it works:**
- Reads the mapping configuration to determine destination paths
- Copies files from temp directory to mapped destinations
- Auto-updates mapping config for new files
- Preserves directory structure in destination

**Usage:**
```bash
python sync_to_destination.py \
  --generated ./temp-docs \
  --destination docs/API-Reference/Product-APIs \
  --mapping .github/doc-mapping.json \
  --changed-list changed_files.txt
```

**Arguments:**
- `--generated`: Directory with generated markdown files (temp location)
- `--destination`: Base destination directory for markdown files
- `--mapping`: Path to mapping configuration file
- `--changed-list`: File containing list of changed YAML files to sync

**Output:**
- Copies/moves files to proper destinations
- Updates mapping configuration if new files are added

---

### 3. `create_individual_prs.py`

**Purpose:** Creates individual pull requests for each changed file with proper file mapping and duplicate prevention.

**How it works:**
- Reads list of changed YAML files
- For each file:
  - Checks if an open PR already exists (skip if so)
  - Creates a new git branch
  - Calls `sync_to_destination.py` to map files to destinations
  - Commits changes to destination paths (not temp paths)
  - Creates a PR with detailed description
- Handles all git operations, error recovery, and branch management

**Usage:**
```bash
python create_individual_prs.py \
  --changed-list changed_files.txt \
  --temp-dir ./temp-docs \
  --dest-dir docs/API-Reference/Product-APIs \
  --mapping-file .github/doc-mapping.json \
  --sync-script .github/scripts/sync_to_destination.py \
  --base-branch master \
  --pr-branch-prefix doc-bot \
  --openai-model gpt-4o \
  --max-iterations 3 \
  --completeness-threshold 90
```

**Arguments:**
- `--changed-list`: File containing list of changed YAML files
- `--temp-dir`: Directory with generated markdown files
- `--dest-dir`: Destination directory for markdown files
- `--mapping-file`: Path to mapping configuration file
- `--sync-script`: Path to sync_to_destination.py script
- `--base-branch`: Base branch to create PRs from (default: master)
- `--pr-branch-prefix`: Branch name prefix for PRs (default: doc-bot)
- `--openai-model`: AI model used (for PR description)
- `--max-iterations`: Max iterations used (for PR description)
- `--completeness-threshold`: Quality threshold (for PR description)

**Output:**
- Creates individual PRs for each file
- Returns exit code 1 if any PRs failed to create
- Prints summary of processed/skipped/failed files

**Features:**
- ✅ Duplicate PR prevention (checks for existing open PRs)
- ✅ Comprehensive error handling and recovery
- ✅ Detailed logging for debugging
- ✅ Git branch management (create/checkout/cleanup)
- ✅ Proper file mapping integration
- ✅ Commits to destination paths, not temp paths

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
2. **Documentation generation** - Action generates markdown to temp directory
3. **create_individual_prs.py** - Creates PRs with proper file mapping
   - Internally calls **sync_to_destination.py** for each file

See `examples/destination-repo/workflows/sync-api-docs.yml` for complete workflow example.

## File Mapping Configuration

All scripts use `.github/doc-mapping.json` for configuration:

```json
{
  "source_base": "api-docs/public",
  "dest_base": "docs/API-Reference/Product-APIs",
  "file_mappings": {
    "AI-Services.yaml": "AI-Services.md",
    "Filesets.yaml": "Filesets.md"
  },
  "default_rule": {
    "pattern": "*.yaml",
    "output": "{basename}.md"
  }
}
```

- `source_base`: Base path in source repo
- `dest_base`: Base path in destination repo
- `file_mappings`: Explicit source → destination mappings
- `default_rule`: Pattern for auto-mapping new files

## Testing Scripts Locally

```bash
# Test detection
python .github/scripts/detect_yaml_changes.py \
  --source ../source-repo/api-docs/public \
  --dest docs/API-Reference/Product-APIs \
  --mapping .github/doc-mapping.json

# Test sync
python .github/scripts/sync_to_destination.py \
  --generated ./temp-docs \
  --destination docs/API-Reference/Product-APIs \
  --mapping .github/doc-mapping.json \
  --changed-list changed_files.txt

# Test PR creation (requires git repo and gh CLI)
export GH_TOKEN="your_token"
python .github/scripts/create_individual_prs.py \
  --changed-list changed_files.txt \
  --temp-dir ./temp-docs \
  --dest-dir docs/API-Reference/Product-APIs \
  --mapping-file .github/doc-mapping.json \
  --sync-script .github/scripts/sync_to_destination.py \
  --base-branch master
```

## Troubleshooting

### Script fails with "command not found"
- Ensure Python 3.7+ is installed: `python --version`
- For `create_individual_prs.py`, ensure `git` and `gh` CLI are installed

### "No changes detected" but files have changed
- Check file modification timestamps
- Verify mapping configuration paths are correct
- Use `--force true` flag with detect_yaml_changes.py

### PR creation fails with authentication error
- Ensure `GH_TOKEN` environment variable is set
- Verify token has required permissions (repo, pull_requests)
- Check GitHub App configuration if using app authentication

### Files end up in wrong destination
- Check `.github/doc-mapping.json` file mappings
- Verify `source_base` and `dest_base` paths are correct
- Review sync script output for mapping details
