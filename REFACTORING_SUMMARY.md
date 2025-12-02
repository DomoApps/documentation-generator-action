# Refactoring Summary: Decoupling PR Creation from Action

## Problem

The GitHub Action (`action.yml`) was tightly coupled with destination-repo-specific logic for creating individual PRs. This caused:

1. **Wrong file locations**: Commits were being made to `temp-docs/AI-Services.md` instead of the proper destination `docs/API-Reference/Product-APIs/AI-Services.md`
2. **Tight coupling**: The action contained logic specific to the cross-repo sync scenario
3. **Bypassed sync**: The individual PR creation flow generated and committed files directly, bypassing the sync script that handles file mapping

## Solution

**Separated concerns** - The action now only generates documentation. The destination repo workflow handles PR creation with proper file mapping.

### Changes to `action.yml`

**Removed:**
- `create_individual_prs` input parameter
- `prevent_duplicate_prs` input parameter
- `pr_branch_prefix` input parameter
- `base_branch` input parameter
- "Filter files with existing PRs" step
- "Create Individual Pull Requests" step (entire 165-line section)
- Individual PR logic from Summary step

**Simplified:**
- "Generate Documentation" step now always runs (no conditional for individual PRs)
- "Create Pull Request" step simplified (no individual PR conditional)
- "Check if processing needed" step simplified (removed PR filtering logic)

**Result:** The action is now **generic and reusable** - it just generates docs and optionally creates a single PR.

### Changes to `examples/destination-repo/workflows/sync-api-docs.yml`

**Modified:**
- "Generate Documentation" step now has `create_pull_request: 'false'` - action only generates, doesn't create PRs
- Removed obsolete parameters: `create_individual_prs`, `prevent_duplicate_prs`, `pr_branch_prefix`, `base_branch`

**Replaced:**
- Inline bash PR creation logic (~150 lines) replaced with call to `create_individual_prs.py` script (~10 lines)

**Result:** File mapping and PR creation logic now lives in the **destination repo** where it belongs.

### New Script: `examples/destination-repo/.github/scripts/create_individual_prs.py`

**Purpose:** Handles individual PR creation with proper file mapping

**Features:**
- Checks for existing open PRs (prevents duplicates)
- Creates/manages git branches
- Calls `sync_to_destination.py` for file mapping
- Commits to destination paths (not temp-docs)
- Creates PRs with detailed descriptions
- Comprehensive error handling and logging
- Returns proper exit codes for CI/CD

**Usage:**
```bash
python .github/scripts/create_individual_prs.py \
  --changed-list changed_files.txt \
  --temp-dir ./temp-docs \
  --dest-dir docs/API-Reference/Product-APIs \
  --mapping-file .github/doc-mapping.json \
  --sync-script .github/scripts/sync_to_destination.py \
  --base-branch master \
  --pr-branch-prefix doc-bot
```

**Result:** PR creation logic is now testable, maintainable Python code instead of inline bash.

## Architecture

### Before (Tight Coupling)

```
Action (action.yml)
├── Generate docs
├── Check for existing PRs          ❌ Destination-specific
├── Create branches                 ❌ Destination-specific
├── Commit to temp-docs             ❌ Wrong location
└── Create individual PRs           ❌ Destination-specific
```

### After (Separation of Concerns)

```
Action (action.yml)                 ✅ Generic, reusable
├── Generate docs to output_path
└── Optional: Create single PR

Destination Repo Workflow          ✅ Handles repo-specific logic
├── Call action to generate
├── For each changed file:
│   ├── Check for existing PR
│   ├── Create branch
│   ├── Run sync script (file mapping)
│   ├── Commit to destination path
│   └── Create PR
```

## Benefits

1. **Correct file locations**: Files are now committed to `docs/API-Reference/Product-APIs/` not `temp-docs/`
2. **Loose coupling**: Action is generic, destination repos customize behavior
3. **File mapping works**: Sync script properly executes before commits
4. **Maintainability**: Destination-specific logic lives in destination repos
5. **Reusability**: Action can be used in any repo without cross-repo assumptions

## Migration Guide

### For existing destination repos using individual PRs:

1. Update workflow to use new approach (see `examples/destination-repo/workflows/sync-api-docs.yml`)
2. Remove these inputs from action call:
   - `create_individual_prs`
   - `prevent_duplicate_prs`
   - `pr_branch_prefix`
   - `base_branch`
3. Set `create_pull_request: 'false'` in action call
4. Add the "Create Individual PRs with File Sync" step after doc generation
5. Customize branch names, base branch, and paths as needed

### For repos using single PR (no changes needed):

The action still supports single PR creation with `create_pull_request: 'true'`. No migration needed.

## Testing Checklist

- [ ] Action generates docs to specified output_path
- [ ] Single PR creation still works (backward compatibility)
- [ ] Individual PR creation in destination workflow works
- [ ] Files are committed to destination paths, not temp-docs
- [ ] File mapping configuration is properly applied
- [ ] Mapping file is updated and committed when new files are added
- [ ] Existing PR detection prevents duplicates
- [ ] Branch creation and management works correctly

## Files Changed

1. `action.yml` - Removed individual PR logic (simplified by ~200 lines)
2. `examples/destination-repo/workflows/sync-api-docs.yml` - Replaced inline bash with script call
3. `examples/destination-repo/.github/scripts/create_individual_prs.py` - New Python script for PR creation
4. `CROSS_REPO_SYNC.md` - Updated to reference new script
5. `REFACTORING_SUMMARY.md` - This document
