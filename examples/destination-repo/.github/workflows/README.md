# Sync Enhanced YAML Workflow

This directory contains an example workflow for automatically enhancing and syncing OpenAPI YAML files from a source repository.

## Overview

The `sync-api-docs.yml` workflow automatically:
1. Detects changed YAML files in the source repository
2. Enhances YAML files with AI-generated descriptions
3. Creates individual PRs per file with duplicate prevention
4. Syncs enhanced YAML files to the destination repository

## Key Features

### 1. AI-Powered YAML Enhancement

Enhances OpenAPI specifications with contextual descriptions for:
- info.description
- Tag descriptions
- Endpoint descriptions
- Parameter descriptions
- Schema descriptions
- Property descriptions

### 2. Individual PRs Per File

```yaml
# Create individual PRs automatically
- python .github/scripts/create_individual_prs.py \
    --changed-list changed_files.txt \
    --temp-dir ./temp-enhanced-yaml \
    --dest-dir docs/API-Reference/Product-APIs \
    --pr-branch-prefix yaml-enhance
```

Each file gets its own PR with branch name: `yaml-enhance/{filename}`

### 3. Automatic Duplicate Prevention

The script checks for existing PRs before creating new ones:
- **Checks for open PRs** by branch name (`yaml-enhance/{filename}`)
- **Skips files** if PR already exists
- **No duplicate PRs** when scheduled workflow runs every 6 hours

### 4. Structure Preservation

All enhancements preserve:
- Original YAML structure
- Comments and formatting
- Key ordering
- Indentation style

## How It Works

### Workflow Flow

```
1. Clone source and destination repos
   ↓
2. Detect changed YAML files (cross-repo comparison)
   ↓
3. Enhance YAML files with AI-generated descriptions
   ↓
4. Check for existing PRs (by branch name)
   ↓
5. Create individual PRs for each file (skip if exists)
   ↓
6. Sync enhanced YAML to destination paths
```

### Duplicate Prevention Logic

```
For each changed file:
  - Check if PR exists for branch: yaml-enhance/{filename}
  - If exists → Skip (log message)
  - If not exists → Create branch, commit, and open PR

Result: No duplicate PRs, clean PR list
```

### Branch Naming Pattern

- Pattern: `{pr_branch_prefix}/{filename-without-extension}`
- Example: `ai.yaml` → branch: `yaml-enhance/ai`
- Consistent naming enables reliable duplicate detection

## Files in This Directory

### Required Files (Copy to Destination Repo)

1. **`.github/workflows/sync-api-docs.yml`**
   - Main workflow file
   - Configure source/destination paths
   - Set schedule and triggers

2. **`.github/scripts/detect_yaml_changes.py`**
   - Cross-repo change detection
   - Compares file timestamps between repos
   - Specific to cross-repo sync pattern

3. **`.github/scripts/sync_to_destination.py`**
   - Copies enhanced YAML to destination paths
   - Simple 1:1 file copying (no mapping needed)
   - Preserves filenames

4. **`.github/scripts/create_individual_prs.py`**
   - Creates individual PRs with duplicate checking
   - Handles git operations and PR creation
   - Uses GitHub CLI (gh)

## Configuration

### Workflow Triggers

1. **Schedule**: Runs every 6 hours automatically
2. **Manual**: Use workflow_dispatch in GitHub UI
3. **Webhook**: Optional repository_dispatch from source repo

### Required Secrets

- `OPENAI_API_KEY` - For AI enhancement generation
- `APP_ID` - GitHub App ID for cross-repo access
- `APP_PRIVATE_KEY` - GitHub App private key

### Customization

Edit `sync-api-docs.yml` to customize:

```yaml
# Source repository
repository: domoinc/internal-domo-apis
path: source-repo

# Source YAML path
yaml_input_path: './source-repo/api-docs/public'

# Destination path
yaml_output_path: './temp-enhanced-yaml'  # Temp location
dest_dir: docs/API-Reference/Product-APIs  # Final destination

# Enhancement settings
enhancement_mode: 'missing_only'  # Only enhance missing descriptions
quality_threshold: '85'  # Minimum quality score (0-100)

# PR settings
pr_branch_prefix: 'yaml-enhance'  # Creates branches: yaml-enhance/filename

# Schedule
cron: '0 */6 * * *'  # Every 6 hours
```

## Action Configuration

### Enhancement Settings

| Input | Description | Default |
|-------|-------------|---------|
| `enhancement_mode` | What to enhance: missing_only, improve_all | `missing_only` |
| `quality_threshold` | Minimum quality score (0-100) | `85` |
| `yaml_output_path` | Output directory (empty for in-place) | `''` |

### Standard Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `openai_model` | AI model to use | `gpt-4o` |
| `max_iterations` | Max refinement iterations | `3` |
| `completeness_threshold` | Overall quality threshold | `90` |
| `process_changed_only` | Only process changed files | `false` |

## Benefits vs Markdown Generation

### YAML Enhancement Approach
- ✅ **Enhanced source files** - Destination has complete, documented YAML
- ✅ **Single source of truth** - YAML files are the documentation
- ✅ **Tool compatibility** - Enhanced YAML works with all OpenAPI tools
- ✅ **Version control** - Track description improvements over time
- ✅ **No format conversion** - YAML in, YAML out
- ✅ **Structure preservation** - Comments and formatting maintained

### Previous Markdown Approach
- ❌ **Separate documentation** - YAML and Markdown could drift
- ❌ **Format conversion** - YAML → Markdown transformation
- ❌ **Maintenance burden** - Two files to maintain per spec
- ❌ **Tool limitations** - Markdown not usable by OpenAPI tools

## File Naming Convention

**Simple 1:1 mapping** - No configuration file needed!

- Source: `source-repo/api-docs/public/ai.yaml`
- Enhanced temp: `temp-enhanced-yaml/ai.yaml`
- Destination: `docs/API-Reference/Product-APIs/ai.yaml`

Files keep the same name throughout the pipeline.

## Troubleshooting

### Duplicate PRs Still Being Created

**Check:**
1. Verify `pr_branch_prefix` is consistent across runs
2. Check branch name pattern in GitHub: `{prefix}/{filename}`
3. Look for closed/merged PRs that might conflict

### YAML Enhancement Fails

**Check:**
1. Verify YAML is valid OpenAPI spec (use validator)
2. Check OpenAI API key is valid and has quota
3. Review enhancement logs for specific errors
4. Try increasing `quality_threshold` if validation failing

### PR Creation Fails

**Check:**
1. Workflow has `pull-requests: write` permission
2. `GH_TOKEN` is properly passed to script
3. Branch protection rules allow bot PRs
4. GitHub CLI (gh) is installed and authenticated

### Enhanced YAML Appears Corrupted

**Check:**
1. Verify ruamel.yaml is installed in action environment
2. Check for special characters or encoding issues in original YAML
3. Review action logs for YAML parsing warnings
4. Test enhancement locally with same YAML file

## Example Workflow Run

```
🔍 Detecting changed YAML files...
  - ai.yaml (NEW)
  - filesets.yaml (MODIFIED)
  - accounts.yaml (UNCHANGED)

📊 2 files need enhancement

🚀 Enhancing YAML files...
  ✅ ai.yaml: 42 enhancements applied
  ✅ filesets.yaml: 18 enhancements applied

📄 Creating Individual PRs
  ---
  Processing: ai.yaml
  Branch: yaml-enhance/ai
  🔄 Synced: ./temp-enhanced-yaml/ai.yaml -> docs/API-Reference/Product-APIs/ai.yaml
  ✅ Created PR: https://github.com/org/repo/pull/456
  ---
  Processing: filesets.yaml
  Branch: yaml-enhance/filesets
  ⏭️ Skipping - PR #455 already exists
  ---

📊 Summary:
  - Total: 2
  - Processed: 1
  - Skipped: 1
  - Failed: 0
```

## What Gets Enhanced

Each YAML file is analyzed for missing or inadequate descriptions:

| Field | Enhancement Type | Example |
|-------|------------------|---------|
| info.description | Overall API purpose | "The AI Services API provides..." |
| tags[].description | Tag grouping purpose | "Endpoints for managing AI models" |
| paths[].description | Endpoint functionality | "Create a new summarization task" |
| parameters[].description | Parameter purpose | "Maximum number of results to return" |
| schemas[].description | Schema purpose | "Configuration for AI reasoning" |
| properties[].description | Property meaning | "Number of input tokens processed" |

All enhancements:
- Use contextual AI to generate appropriate descriptions
- Maintain consistency with existing descriptions
- Undergo quality validation (default: 85% threshold)
- Preserve YAML structure and comments

## Best Practices

1. **Review PRs promptly** - Check AI-generated descriptions for accuracy
2. **Merge frequently** - Keep destination YAML up to date
3. **Monitor API usage** - Track OpenAI API quota and costs
4. **Test enhancements** - Validate enhanced YAML with OpenAPI tools
5. **Close stale PRs** - If source changes are reverted
6. **Adjust quality threshold** - Increase if descriptions are low quality

## Migration from Markdown Generation

If you're migrating from the old Markdown generation workflow:

1. **Update action inputs**:
   - Remove: `output_path`, `template_path`
   - Add: `yaml_output_path`, `enhancement_mode`, `quality_threshold`

2. **Update scripts**:
   - Replace all scripts in `.github/scripts/` with new versions
   - Remove `doc-mapping.json` (no longer needed)

3. **Update workflow**:
   - Change temp directory from `temp-docs` to `temp-enhanced-yaml`
   - Update PR branch prefix from `doc-bot` to `yaml-enhance`
   - Remove template setup step

4. **Test thoroughly**:
   - Run manual workflow dispatch first
   - Verify enhanced YAML is valid
   - Check PR creation works correctly

## Support

For issues with the YAML enhancement action:
- Action repository: https://github.com/DomoApps/documentation-generator-action
- Report issues: https://github.com/DomoApps/documentation-generator-action/issues

For issues with the destination repo scripts:
- Check script logs in workflow run
- Review GitHub Actions workflow syntax
- Verify all required secrets are configured
