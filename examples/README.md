# Example Cross-Repository Sync Setup

This directory contains example files for setting up cross-repository documentation synchronization.

## Directory Structure

```
examples/
├── destination-repo/          # Files for the destination repository
│   ├── workflows/
│   │   └── sync-api-docs.yml           # Main sync workflow
│   ├── scripts/
│   │   ├── detect_yaml_changes.py      # Change detection script
│   │   └── sync_to_destination.py      # File sync script
│   └── doc-mapping.json                # File mapping configuration
│
└── source-repo/               # Files for the source repository (OPTIONAL)
    └── workflows/
        └── source-repo-notify.yml      # Notification workflow
```

## Setup Instructions

### Destination Repository (Required)

Copy these files to your destination repository (e.g., `DomoApps/domo-developer-portal`):

```bash
# In your destination repo
mkdir -p .github/workflows .github/scripts

# Copy files from this repo
cp examples/destination-repo/workflows/sync-api-docs.yml .github/workflows/
cp examples/destination-repo/scripts/*.py .github/scripts/
cp examples/destination-repo/doc-mapping.json .github/
```

**Required secrets in destination repo:**
- `APP_ID` - GitHub App ID
- `APP_PRIVATE_KEY` - GitHub App private key
- `OPENAI_API_KEY` - OpenAI API key

See [GITHUB_APP_SETUP.md](../.github/GITHUB_APP_SETUP.md) for detailed setup instructions.

### Source Repository (Optional)

**⚠️ Only needed if you want real-time notifications!**

If you cannot add secrets to your source repository, skip this section. The destination workflow runs on a schedule (every 6 hours) and doesn't require source repo configuration.

If you want to enable real-time notifications:

```bash
# In your source repo (e.g., domoinc/internal-domo-apis)
mkdir -p .github/workflows

# Copy notification workflow
cp examples/source-repo/workflows/source-repo-notify.yml .github/workflows/
```

**Required secrets in source repo:**
- `APP_ID` - GitHub App ID (same as destination)
- `APP_PRIVATE_KEY` - GitHub App private key (same as destination)

## Documentation

- [Cross-Repository Sync Guide](../CROSS_REPO_SYNC.md) - Overview and setup
- [GitHub App Setup Guide](../.github/GITHUB_APP_SETUP.md) - Detailed GitHub App configuration
- [Main README](../README.md) - Action usage and configuration

## How It Works

### Scheduled Polling (Default)

The destination repo workflow runs every 6 hours:
1. Clones the source repository
2. Detects changed YAML files by comparing timestamps
3. Generates markdown documentation using AI
4. Creates a pull request with updates

**No source repo configuration needed!**

### Real-time Notifications (Optional)

If you set up the source repo workflow:
1. Source repo detects YAML file changes
2. Sends `repository_dispatch` event to destination
3. Destination workflow runs immediately (instead of waiting for schedule)

## Customization

### Adjust Sync Schedule

Edit `sync-api-docs.yml` in destination repo:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours (current)
  # Examples:
  # - cron: '0 * * * *'    # Every hour
  # - cron: '0 0 * * *'    # Once per day at midnight
```

### Customize File Mapping

Edit `doc-mapping.json` in destination repo:

```json
{
  "source_base": "api-docs/public",
  "dest_base": "docs/API-Reference/Product-APIs",
  "file_mappings": {
    "AI-Services.yaml": "AI-Services.md",
    "Custom-Name.yaml": "Different-Output-Name.md"
  },
  "default_rule": {
    "pattern": "*.yaml",
    "output": "{basename}.md"
  }
}
```

## Troubleshooting

### Workflow doesn't run

Check that:
- GitHub App is installed on both repositories
- Secrets are correctly set in destination repo
- Destination folder exists (`docs/API-Reference/Product-APIs/`)

### Change detection issues

The change detection compares file modification timestamps. If timestamps aren't reliable:

1. Use manual trigger with "Force regenerate all docs" option
2. Or adjust the detection script logic in `detect_yaml_changes.py`

### Need help?

See the full guides:
- [CROSS_REPO_SYNC.md](../CROSS_REPO_SYNC.md)
- [GITHUB_APP_SETUP.md](../.github/GITHUB_APP_SETUP.md)
