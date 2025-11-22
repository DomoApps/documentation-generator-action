# Sync API Documentation Workflow

This directory contains an example workflow for automatically syncing API documentation from a source repository.

## Overview

The `sync-api-docs.yml` workflow automatically:
1. Detects changed YAML files in the source repository
2. Generates markdown documentation using the documentation-generator-action
3. **Creates individual PRs per file** with duplicate prevention
4. Syncs generated docs to the destination repository structure

## Key Features

### 1. Built-in Individual PRs

The action now handles individual PR creation natively! Simply set:
```yaml
create_individual_prs: 'true'
pr_branch_prefix: 'doc-bot'
```

Each file gets its own PR with branch name: `doc-bot/{filename}`

### 2. Automatic Duplicate Prevention

The action checks for existing PRs **before** generating documentation:
- **Checks for open PRs** by branch name (`doc-bot/{filename}`)
- **Skips document generation** if PR already exists (saves API costs!)
- **No duplicate PRs** when scheduled workflow runs every 6 hours

Set `prevent_duplicate_prs: 'true'` (default) to enable this behavior.

### 3. Simple Configuration

The entire workflow is now **~130 lines** with the action doing all the heavy lifting:

```yaml
- name: Generate Documentation and Create PRs
  uses: DomoApps/documentation-generator-action@main
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    yaml_input_path: './source-repo/api-docs/public'
    output_path: './temp-docs'
    create_pull_request: 'true'
    create_individual_prs: 'true'   # Individual PR per file
    prevent_duplicate_prs: 'true'   # Skip files with existing PRs
    pr_branch_prefix: 'doc-bot'     # Branch naming: doc-bot/{filename}
```

## How It Works

### Workflow Flow

```
1. Clone source and destination repos
   ↓
2. Detect changed YAML files (cross-repo comparison)
   ↓
3. Action checks for existing PRs (by branch name)
   ↓
4. Generate docs ONLY for files without existing PRs ⚡
   ↓
5. Create individual PRs for newly generated docs
   ↓
6. Sync to destination directory structure
```

### Duplicate Prevention Logic

**Before generating documentation** (saves time and money):
```
For each changed file:
  - Check if PR exists for branch: doc-bot/{filename}
  - If exists → Skip (log to summary)
  - If not exists → Add to generation queue

Generate docs only for files in queue
Create PRs for newly generated docs
```

### Branch Naming Pattern

- Pattern: `{pr_branch_prefix}/{filename}`
- Example: `filesets.yaml` → branch: `doc-bot/filesets`
- Consistent naming enables reliable duplicate detection

## Files in This Directory

### Required Files (Copy to Destination Repo)

1. **`.github/workflows/sync-api-docs.yml`**
   - Main workflow file
   - Configure source/destination paths
   - Set schedule and triggers

2. **`.github/scripts/detect_yaml_changes.py`**
   - Cross-repo change detection
   - Compares file timestamps/hashes between repos
   - Specific to cross-repo sync pattern

3. **`.github/scripts/sync_to_destination.py`**
   - Maps generated docs to destination paths
   - Updates mapping configuration
   - Handles directory structure differences

4. **`.github/doc-mapping.json`**
   - Configuration for file path mapping
   - Tracks source → destination relationships

## Configuration

### Workflow Triggers

1. **Schedule**: Runs every 6 hours automatically
2. **Manual**: Use workflow_dispatch in GitHub UI
3. **Webhook**: Optional repository_dispatch from source repo

### Required Secrets

- `OPENAI_API_KEY` - For AI document generation
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
destination: docs/API-Reference/Product-APIs

# PR branch prefix
pr_branch_prefix: 'doc-bot'  # Creates branches: doc-bot/filename

# Schedule
cron: '0 */6 * * *'  # Every 6 hours
```

## Action Inputs Reference

### Individual PR Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `create_individual_prs` | Create separate PR per file | `false` |
| `prevent_duplicate_prs` | Check for existing PRs before generation | `true` |
| `pr_branch_prefix` | Branch name prefix (e.g., "doc-bot") | `doc-bot` |

### Standard Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `create_pull_request` | Enable PR creation | `false` |
| `process_changed_only` | Only process changed files | `false` |
| `openai_model` | AI model to use | `gpt-4o` |
| `max_iterations` | Max refinement iterations | `10` |

## Benefits vs Old Approach

### Old Approach (Manual PR Logic)
- ❌ Complex bash scripts in workflow (~260 lines)
- ❌ Duplicate PR checking AFTER generation
- ❌ Wasted API calls for files with existing PRs
- ❌ Hard to maintain across multiple repos
- ❌ Custom scripts needed per repo

### New Approach (Built-in to Action)
- ✅ Simple workflow configuration (~130 lines)
- ✅ Check PRs BEFORE generation (saves money!)
- ✅ All logic in action repo (one place to update)
- ✅ Reusable across all repos
- ✅ No custom scripts needed

## Troubleshooting

### Duplicate PRs Still Being Created

**Check:**
1. Verify `prevent_duplicate_prs: 'true'` is set
2. Ensure `pr_branch_prefix` matches across runs
3. Check branch name pattern in GitHub: `{prefix}/{filename}`

### Documentation Not Generated

**Check:**
1. Review "Filter files with existing PRs" step output
2. Check if all files have existing PRs (all skipped)
3. Try `force_regenerate: true` in manual dispatch

### PR Creation Fails

**Check:**
1. Workflow has `pull-requests: write` permission
2. `GH_TOKEN` is properly passed to action
3. Branch protection rules allow bot PRs

## Example Workflow Run

```
🔍 Detecting changed YAML files...
  - filesets.yaml
  - accounts.yaml
  - datasets.yaml

🔍 Checking for existing PRs...
  ⏭️ Skipping filesets.yaml (PR #123 already exists)
  ✅ Will process accounts.yaml (no existing PR)
  ✅ Will process datasets.yaml (no existing PR)

🚀 Starting documentation generation...
  ⏭️ Skipped 1 file(s) with existing PRs
  ✅ Generated 2 markdown file(s)

📄 Creating Individual PRs
  ✅ Created PR for accounts.yaml
  ✅ Created PR for datasets.yaml

📊 Summary
  - Total Files: 3
  - PRs Created: 2
  - Skipped: 1
  - Failed: 0
```

## Migration from Old Workflow

If you're migrating from the old complex workflow:

1. **Replace workflow file** with new simplified version
2. **Remove** `check_existing_prs.py` script (built into action now)
3. **Keep** `detect_yaml_changes.py` and `sync_to_destination.py` (still needed for cross-repo)
4. **Update action version** to `@main` or latest release
5. **Test** with manual workflow dispatch first

## Best Practices

1. **Review PRs promptly** - Reduces accumulation of open PRs
2. **Merge frequently** - Keeps documentation up to date
3. **Monitor workflow runs** - Check for API quota issues
4. **Use branch protection** - Require reviews for doc changes
5. **Close stale PRs** - If source changes are reverted
