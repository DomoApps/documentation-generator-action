# Cross-Repository Documentation Sync

This document explains how to set up and use the cross-repository documentation synchronization system.

## Overview

This system automatically syncs API documentation between two repositories:

- **Source Repository**: `domoinc/internal-domo-apis` (contains OpenAPI YAML specs)
- **Destination Repository**: `DomoApps/domo-developer-portal` (contains generated markdown docs)

### How It Works

**Primary Method: Scheduled Polling (Recommended)**

```
┌─────────────────────────────────────────────────────────────────┐
│  Destination Repo (domo-developer-portal)                       │
│                                                                  │
│  1. Scheduled workflow runs every 6 hours (configurable)        │
│  2. Clones source repo (domoinc/internal-domo-apis)             │
│  3. Detects changed YAML files (compares timestamps)            │
│  4. Generates markdown documentation using AI                   │
│  5. Maps files to destination paths                             │
│  6. Updates mapping configuration (if new files)                │
│  7. Creates PR with generated docs                              │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ No secrets required in source repo
- ✅ Works with any organization permissions
- ✅ Simpler setup and maintenance
- ✅ All control in one place

**Alternative Method: Real-time Notifications (Optional)**

```
┌─────────────────────────────────────────────────────────────────┐
│  Source Repo (internal-domo-apis)                               │
│                                                                  │
│  1. Developer pushes YAML changes to api-docs/public/           │
│  2. GitHub Action triggers notification workflow                │
│  3. Sends repository_dispatch to destination repo               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Destination Repo (domo-developer-portal)                       │
│                                                                  │
│  4. Receives dispatch event, starts sync workflow               │
│  5. Clones source repo                                          │
│  6. Detects changed YAML files                                  │
│  7. Generates markdown documentation using AI                   │
│  8. Maps files to destination paths                             │
│  9. Updates mapping configuration (if new files)                │
│  10. Creates PR with generated docs                             │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Immediate notification when source changes
- ✅ Lower Actions minutes usage

**Drawbacks:**
- ⚠️ Requires secrets in source repo
- ⚠️ May not work with strict organization policies

## Setup Instructions

### 1. Destination Repository Setup (domo-developer-portal)

The destination repository needs these files (already created in this repo):

```
.github/
├── workflows/
│   └── sync-api-docs.yml           # Main sync workflow
├── scripts/
│   ├── detect_yaml_changes.py      # Detects changed files
│   └── sync_to_destination.py      # Syncs to destination
└── doc-mapping.json                 # File mapping configuration
```

**Required Secrets:**
- `OPENAI_API_KEY` - OpenAI API key for documentation generation
- `APP_ID` - GitHub App ID for authentication
- `APP_PRIVATE_KEY` - GitHub App private key for authentication

To add secrets:
1. Go to repo Settings → Secrets and variables → Actions
2. Add `OPENAI_API_KEY` (get from OpenAI dashboard)
3. Add `APP_ID` and `APP_PRIVATE_KEY` (see [GitHub App Setup Guide](.github/GITHUB_APP_SETUP.md))

**Note:** Using a GitHub App is more secure than Personal Access Tokens (PATs). See the [GitHub App Setup Guide](.github/GITHUB_APP_SETUP.md) for detailed instructions.

### 2. Source Repository Setup (internal-domo-apis) - OPTIONAL

**⚠️ This step is OPTIONAL and only needed for real-time notifications!**

If you cannot add secrets to the source repository (e.g., organization restrictions), skip this section. The destination workflow will run on a schedule (every 6 hours by default) and doesn't require source repo configuration.

**Only proceed if:**
- You want real-time notifications when YAML files change
- You have permission to add secrets to the source repository

Copy the notification workflow to the source repository:

```bash
# In the source repo (internal-domo-apis)
mkdir -p .github/workflows
cp /path/to/this/repo/.github/workflows/source-repo-notify.yml \
   .github/workflows/notify-doc-sync.yml
```

**Required Secrets:**
- `APP_ID` - GitHub App ID (same as destination repo)
- `APP_PRIVATE_KEY` - GitHub App private key (same as destination repo)

See the [GitHub App Setup Guide](.github/GITHUB_APP_SETUP.md) for instructions on adding these secrets.

### 3. File Mapping Configuration

The `.github/doc-mapping.json` file controls how source files map to destination files:

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

**Key concepts:**
- `source_base`: Base path in source repo where YAML files live
- `dest_base`: Base path in dest repo where markdown files go
- `file_mappings`: Explicit source → destination mappings
- `default_rule`: Pattern for auto-mapping new files

**Auto-mapping**: When a new YAML file is detected, it's automatically mapped using the default rule and added to `file_mappings`.

## Usage

### Automatic Sync (Recommended)

The sync happens automatically when:

1. **On Push**: Developer pushes YAML changes to source repo
   - Workflow triggers immediately via `repository_dispatch`

2. **Scheduled**: Every 6 hours as a safety net
   - Catches any missed changes
   - Ensures docs stay up-to-date

### Manual Trigger

You can manually trigger the sync workflow:

1. Go to destination repo → Actions → "Sync API Documentation from Source Repo"
2. Click "Run workflow"
3. Optionally check "Force regenerate all docs" to regenerate everything

### What Happens in the PR

When changes are detected, a PR is created with:

**Modified Files:**
- `docs/API-Reference/Product-APIs/*.md` - Generated documentation
- `.github/doc-mapping.json` - Updated mappings (if new files added)

**PR Description Includes:**
- Summary of changes (new files, modified files, unchanged files)
- List of processed YAML files
- Automatic assignment to workflow trigger

**Example PR:**
```markdown
## 🤖 Auto-Generated Documentation Sync

### 📊 Changes Summary
**Total files requiring update:** 3

**New Files (1):**
- 🆕 `Activity-Log.yaml`

**Modified Files (2):**
- 📝 `AI-Services.yaml`
- 📝 `Filesets.yaml`

### ✅ Actions Taken
- Detected changed YAML files in source repository
- Generated markdown documentation using AI
- Mapped files to destination paths
- Updated mapping configuration (1 new file added)
```

## File Mapping Examples

### Example 1: Simple Mapping (Default Rule)

**Source**: `api-docs/public/NewAPI.yaml`
**Destination**: `docs/API-Reference/Product-APIs/NewAPI.md`
**Mapping**: Auto-generated using `{basename}.md` rule

### Example 2: Custom Mapping

To map a file to a different name, manually edit `.github/doc-mapping.json`:

```json
{
  "file_mappings": {
    "AI-Services.yaml": "AI-Services.md",
    "legacy-api.yaml": "Legacy-API-v1.md"  // Custom name
  }
}
```

### Example 3: Subdirectory Structure

If you have subdirectories in source and want to preserve them:

```json
{
  "source_base": "api-docs/public",
  "dest_base": "docs/API-Reference/Product-APIs",
  "file_mappings": {
    "v1/Users.yaml": "v1/Users.md",
    "v2/Users.yaml": "v2/Users.md"
  }
}
```

The scripts will automatically create subdirectories in the destination.

## Monitoring & Debugging

### Check Workflow Status

**In Destination Repo:**
- Go to Actions → "Sync API Documentation from Source Repo"
- View recent runs to see if sync succeeded

**In Source Repo:**
- Go to Actions → "Notify Documentation Sync"
- Verify notification was sent

### Common Issues

**Issue**: No PR created after source repo push

**Solution**:
1. Check source repo workflow ran successfully
2. Verify `DEST_REPO_PAT` secret is set correctly
3. Check destination repo received `repository_dispatch` event
4. Review destination workflow logs

**Issue**: PR created but files in wrong location

**Solution**:
1. Check `.github/doc-mapping.json` configuration
2. Verify `source_base` and `dest_base` paths are correct
3. Update mapping manually if needed

**Issue**: Documentation quality issues

**Solution**:
1. Check OpenAI API key is valid
2. Review YAML source file for completeness
3. Adjust `MAX_ITERATIONS` or `COMPLETENESS_THRESHOLD` in action inputs
4. Review generated docs in PR before merging

### Logs & Debugging

The workflow outputs detailed logs at each step:

```
Detection complete: 3 files need regeneration
NEW: Activity-Log.yaml -> Activity-Log.md
MODIFIED: AI-Services.yaml (source newer than dest)
SYNCED: ./temp-docs/AI-Services.md -> docs/API-Reference/Product-APIs/AI-Services.md
```

## Advanced Configuration

### Customizing Documentation Generation

Edit `.github/workflows/sync-api-docs.yml` to adjust AI generation parameters:

```yaml
- name: Generate Documentation
  uses: DomoApps/documentation-generator-action@main
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    openai_model: 'gpt-4o'  # Change model
    max_iterations: '5'      # Increase refinement iterations
    completeness_threshold: '95'  # Higher quality bar
```

### Filtering Which Files to Process

To only process specific files or directories, update the path filters in both workflows:

**Source Repo** (notify-doc-sync.yml):
```yaml
paths:
  - 'api-docs/public/v2/**/*.yaml'  # Only v2 APIs
```

**Destination Repo** (sync-api-docs.yml):
The scripts will automatically filter based on source base path.

### Custom PR Labels & Assignees

Edit sync-api-docs.yml:

```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v5
  with:
    labels: |
      documentation
      auto-generated
      api-sync
    assignees: team-docs,api-team
    reviewers: senior-dev
```

## Maintenance

### Updating the Mapping Configuration

The mapping configuration is version controlled. To update:

1. Edit `.github/doc-mapping.json` in destination repo
2. Commit and push changes
3. Next sync will use updated mappings

### Removing Old Mappings

Old mappings are preserved for backward compatibility. To clean up:

1. Identify obsolete mappings (source files deleted)
2. Remove entries from `file_mappings`
3. Manually delete corresponding markdown files if needed

### Updating Scripts

The Python scripts (detect, sync) can be updated directly in `.github/scripts/`. Changes take effect immediately on next workflow run.

## Troubleshooting

### Test the Detection Script Locally

```bash
python .github/scripts/detect_yaml_changes.py \
  --source /path/to/source/repo/api-docs/public \
  --dest /path/to/dest/repo/docs/API-Reference/Product-APIs \
  --mapping .github/doc-mapping.json
```

### Test the Sync Script Locally

```bash
python .github/scripts/sync_to_destination.py \
  --generated ./temp-docs \
  --destination ./docs/API-Reference/Product-APIs \
  --mapping .github/doc-mapping.json \
  --changed-list changed_files.txt
```

### Dry Run Mode

To test without making changes, add `--dry-run` flag support to scripts (future enhancement).

## Security Considerations

- **PAT Permissions**: Use fine-grained PATs with minimum required permissions
- **Secret Rotation**: Rotate `SOURCE_REPO_PAT` and `DEST_REPO_PAT` regularly
- **OpenAI API**: Monitor API usage and set spending limits
- **PR Review**: Always review auto-generated PRs before merging
- **Branch Protection**: Enable branch protection on destination repo main branch

## Support

For issues or questions:
1. Check workflow logs in GitHub Actions
2. Review this documentation
3. Create issue in destination repo with workflow run link
