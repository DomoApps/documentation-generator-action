# Cross-Repo Sync Setup Summary

## ✅ Files Created

### Destination Repository Files (Current Repo)

1. **`.github/workflows/sync-api-docs.yml`**
   - Main orchestration workflow
   - Triggers: repository_dispatch, manual, scheduled
   - Clones source, detects changes, generates docs, creates PR

2. **`.github/scripts/detect_yaml_changes.py`**
   - Compares source YAML vs destination MD files
   - Detects new, modified, and unchanged files
   - Outputs list for processing

3. **`.github/scripts/sync_to_destination.py`**
   - Maps generated markdown to destination paths
   - Auto-updates mapping config for new files
   - Copies files maintaining structure

4. **`.github/doc-mapping.json`**
   - Configuration for source → destination file mappings
   - Auto-updated when new files detected
   - Version controlled for audit trail

5. **`CROSS_REPO_SYNC.md`**
   - Comprehensive documentation
   - Setup instructions
   - Usage guide
   - Troubleshooting

### Source Repository Files (To Be Copied)

6. **`.github/workflows/source-repo-notify.yml`**
   - Simple notification workflow
   - Copy to `domoinc/internal-domo-apis`
   - Triggers repository_dispatch on push

## 🚀 Next Steps

### 1. Deploy to Destination Repo (domo-developer-portal)

```bash
# These files are already in this repo and ready to push
git add .github/
git add CROSS_REPO_SYNC.md
git commit -m "feat: add cross-repo documentation sync system"
git push
```

### 2. Configure Secrets in Destination Repo

Go to Settings → Secrets and variables → Actions:

- **`OPENAI_API_KEY`**: Your OpenAI API key
- **`SOURCE_REPO_PAT`**: GitHub PAT with access to source repo
  - Needs `repo` scope
  - Must have access to `domoinc/internal-domo-apis`

### 3. Deploy to Source Repo (internal-domo-apis)

```bash
# In the internal-domo-apis repo
mkdir -p .github/workflows

# Copy the notification workflow
cp /path/to/this/repo/.github/workflows/source-repo-notify.yml \
   .github/workflows/notify-doc-sync.yml

git add .github/workflows/notify-doc-sync.yml
git commit -m "feat: add documentation sync notification workflow"
git push
```

### 4. Configure Secret in Source Repo

Go to Settings → Secrets and variables → Actions:

- **`DEST_REPO_PAT`**: GitHub PAT with access to destination repo
  - Needs `repo` scope
  - Must have access to `DomoApps/domo-developer-portal`

## 🧪 Testing

### Test the System End-to-End

1. **Make a test change in source repo:**
   ```bash
   # In internal-domo-apis
   echo "# test change" >> api-docs/public/AI-Services.yaml
   git add api-docs/public/AI-Services.yaml
   git commit -m "test: trigger doc sync"
   git push
   ```

2. **Verify notification sent:**
   - Go to Actions in source repo
   - Check "Notify Documentation Sync" workflow ran

3. **Verify sync triggered:**
   - Go to Actions in destination repo
   - Check "Sync API Documentation from Source Repo" workflow started
   - Review logs for each step

4. **Check PR created:**
   - Go to Pull Requests in destination repo
   - Should see PR with title "📚 Sync API Documentation from internal-domo-apis"
   - Review changes

5. **Merge PR:**
   - Review generated documentation
   - Check mapping config updates
   - Merge when satisfied

### Test Manual Trigger

1. Go to destination repo → Actions
2. Select "Sync API Documentation from Source Repo"
3. Click "Run workflow"
4. Check "Force regenerate all docs" to test full regeneration
5. Monitor workflow execution

## 📊 Expected Workflow

### Normal Operation

```
Source Repo Push → Notification → Destination Sync → PR Created → Review → Merge
     (1min)          (instant)        (5-10min)       (instant)
```

### Scheduled Sync (Backup)

```
Every 6 hours → Check for changes → Generate if needed → PR if changes
```

## 🔍 Monitoring

### Key Metrics to Watch

1. **Sync Success Rate**: Workflows → Filter by "Sync API Documentation"
2. **PR Merge Time**: Pull Requests → Filter by label "documentation"
3. **Generation Quality**: Review AI validation scores in workflow logs
4. **Mapping Accuracy**: Check that files land in correct locations

### Alerting (Optional)

Set up GitHub notifications:
- Settings → Notifications
- Enable for "Actions: Failed workflow run"

## 📝 Maintenance Checklist

### Weekly
- [ ] Review recent sync PRs for quality
- [ ] Check workflow success rate
- [ ] Verify no failed runs

### Monthly
- [ ] Review mapping configuration
- [ ] Clean up obsolete mappings
- [ ] Check OpenAI API usage/costs
- [ ] Rotate PAT tokens

### Quarterly
- [ ] Review and update documentation
- [ ] Test disaster recovery (manual sync)
- [ ] Update action versions in workflows

## 🎯 Success Criteria

The system is working correctly when:

✅ Source repo changes trigger destination sync automatically
✅ PRs are created within 10 minutes of source push
✅ Generated documentation meets quality standards (90%+ score)
✅ New files are automatically mapped correctly
✅ Mapping configuration stays up-to-date
✅ No manual intervention needed for standard updates

## 📞 Support

Questions or issues? Check:
1. `CROSS_REPO_SYNC.md` - Full documentation
2. Workflow logs - Detailed execution info
3. This summary - Quick reference
