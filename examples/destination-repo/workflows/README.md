# Sync API Documentation Workflow

This directory contains the workflow for automatically syncing API documentation from the source repository.

## Overview

The `sync-api-docs.yml` workflow automatically:
1. Detects changed YAML files in the source repository
2. Generates markdown documentation for each changed file
3. Creates **individual pull requests** for each file
4. Prevents duplicate PRs when the workflow runs on a schedule

## Key Features

### 1. Individual PRs per File

Each changed YAML file gets its own dedicated pull request. This provides:

- **Easier reviews**: Reviewers can focus on one API at a time
- **Independent merging**: Files can be reviewed and merged independently
- **Better tracking**: Each API change has its own discussion thread
- **Clearer history**: Git history shows exactly which API changed when

**Branch naming pattern**: `docs/sync-api-docs-{filename}`

Example:
- `filesets.yaml` → branch: `docs/sync-api-docs-filesets`
- `accounts.yaml` → branch: `docs/sync-api-docs-accounts`

### 2. Duplicate PR Prevention

The workflow checks for existing PRs before creating new ones:

- **Before processing each file**: Uses `check_existing_prs.py` to query open PRs
- **If PR exists**: Skips processing and logs "PR already exists"
- **If PR doesn't exist**: Generates docs and creates new PR
- **If branch exists but PR closed**: Updates the branch and creates new PR

This prevents the scheduled workflow (runs every 6 hours) from creating duplicate PRs.

## How It Works

### Workflow Triggers

1. **Schedule**: Runs every 6 hours automatically
2. **Manual**: Use workflow_dispatch to run on demand
3. **Source notification**: Optional repository_dispatch from source repo

### Processing Steps

For each changed file:

```
1. Check if PR already exists for this file
   ├─ If yes: Skip (log to summary)
   └─ If no: Continue to step 2

2. Generate documentation
   └─ Run doc_generator_main.py for this file only

3. Sync to destination
   └─ Copy generated docs to docs/API-Reference/Product-APIs

4. Create or update PR
   ├─ Check if branch exists
   ├─ Create/update branch
   ├─ Commit changes
   ├─ Push to remote
   └─ Create PR (if doesn't exist) or update existing

5. Cleanup temporary files
```

### Output Summary

The workflow provides detailed summary with:
- Total files detected
- PRs created/updated
- PRs skipped (already exist)
- Failed operations

## Scripts

### `check_existing_prs.py`

Checks if a PR already exists for a specific file.

**Usage**:
```bash
python .github/scripts/check_existing_prs.py \
  --file-name filesets.yaml \
  --branch-prefix docs/sync-api-docs
```

**Exit codes**:
- `0`: No PR exists (safe to create)
- `1`: PR already exists (skip creation)

**Output** (text mode):
```
✓ PR already exists for filesets.yaml
  Branch: docs/sync-api-docs-filesets
  PR #123: 📚 Sync documentation for filesets.yaml
  URL: https://github.com/org/repo/pull/123
```

## Configuration

The workflow is configured to:

- **Source repository**: `domoinc/internal-domo-apis`
- **Source path**: `api-docs/public/`
- **Destination path**: `docs/API-Reference/Product-APIs`
- **Branch prefix**: `docs/sync-api-docs-`
- **AI Model**: `gpt-4o`

## Troubleshooting

### Duplicate PRs still being created

**Cause**: The `check_existing_prs.py` script might not be finding existing PRs.

**Solution**:
1. Verify branch naming is consistent
2. Check that `gh` CLI is authenticated
3. Review the workflow logs for error messages

### Files not being processed

**Cause**: The change detection might not be detecting the files.

**Solution**:
1. Check the "Detect Changed YAML Files" step output
2. Verify the source path configuration
3. Use `force_regenerate: true` in manual workflow dispatch

### Documentation not updating

**Cause**: The sync script might be failing.

**Solution**:
1. Check the "Sync to Destination" step logs
2. Verify mapping configuration in `.github/doc-mapping.json`
3. Ensure destination paths exist

## Migration from Old Workflow

### Old Behavior (Single PR)
- Processed all changed files at once
- Created one PR with all changes
- No duplicate prevention
- Hard to review multiple APIs at once

### New Behavior (Individual PRs)
- Processes each file separately
- Creates individual PR per file
- Prevents duplicate PRs
- Easy to review and merge independently

### What Changed

1. **Removed**: Single bulk processing step
2. **Added**: Loop that processes each file individually
3. **Added**: PR existence check before creation
4. **Added**: Per-file branch naming
5. **Added**: Detailed processing summary

## Example Workflow Run

```
📊 Processing Summary
- Total Files: 3
- Processed (PRs created/updated): 2
- Skipped (existing PRs): 1
- Failed: 0

---

### 📄 Processing: filesets.yaml
- Status: Creating new PR
- Result: ✅ PR created successfully

### 📄 Processing: accounts.yaml
- Status: ⏭️ Skipped (PR already exists)

### 📄 Processing: datasets.yaml
- Status: Creating new PR
- Result: ✅ PR created successfully
```

## Best Practices

1. **Review PRs promptly**: Reduces accumulation of open PRs
2. **Merge frequently**: Keeps documentation up to date
3. **Close stale PRs**: If API changes are no longer needed
4. **Monitor workflow runs**: Check the summary for failures

## Future Enhancements

Potential improvements:
- Auto-close PRs for deleted source files
- Add labels to PRs based on API type
- Notify specific reviewers per API
- Auto-merge if quality checks pass
