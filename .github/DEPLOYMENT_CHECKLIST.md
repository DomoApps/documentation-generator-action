# Deployment Checklist for Cross-Repo Sync

## Pre-Deployment Setup

### 1. Create GitHub App (RECOMMENDED)

**Follow the comprehensive guide:** [`.github/GITHUB_APP_SETUP.md`](.github/GITHUB_APP_SETUP.md)

**Quick summary:**
1. Create GitHub App in organization settings
2. Set permissions: Contents (R/W), Workflows (R/W), Pull Requests (R/W)
3. Generate private key (`.pem` file)
4. Install app on both repositories
5. Save App ID and private key for secrets

**Benefits over PATs:**
- ✅ Organization-owned (not tied to a user)
- ✅ Auto-rotating tokens (more secure)
- ✅ Fine-grained repository access
- ✅ Better audit trail

### 2. Get OpenAI API Key

- **Purpose**: Generate documentation using AI
- **Where to get**: https://platform.openai.com/api-keys
- **Recommended**: Create a new key specifically for this project
- **Name it**: "domo-developer-portal-docs-sync"

---

## Deployment Steps

### Step 1: Deploy to Destination Repo (`DomoApps/domo-developer-portal`)

#### A. Add GitHub Secrets

1. Go to `DomoApps/domo-developer-portal`
2. Navigate to: Settings → Secrets and variables → Actions → New repository secret
3. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `APP_ID` | `123456` | Your GitHub App ID |
| `APP_PRIVATE_KEY` | `-----BEGIN RSA PRIVATE KEY-----\n...` | Contents of `.pem` file (including BEGIN/END lines) |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key |

#### B. Push Workflow Files

```bash
# In this repo (documentation-generator-action)
git status  # Verify the files to be committed

# Add the new files
git add .github/workflows/sync-api-docs.yml
git add .github/scripts/detect_yaml_changes.py
git add .github/scripts/sync_to_destination.py
git add .github/doc-mapping.json
git add .github/CROSS_REPO_SETUP_SUMMARY.md
git add .github/DEPLOYMENT_CHECKLIST.md
git add CROSS_REPO_SYNC.md
git add README.md

# Commit
git commit -m "feat: add cross-repository documentation sync system

- Add workflow to sync docs from internal-domo-apis
- Add Python scripts for change detection and file mapping
- Add configuration for file mappings
- Add comprehensive documentation
- Update README with new feature"

# Push to main (or your working branch)
git push origin main
```

#### C. Verify Deployment

- [ ] Go to Actions tab in `DomoApps/domo-developer-portal`
- [ ] Confirm "Sync API Documentation from Source Repo" workflow appears
- [ ] Check it's not showing any errors

---

### Step 2: Deploy to Source Repo (`domoinc/internal-domo-apis`)

#### A. Add GitHub Secrets

1. Go to `domoinc/internal-domo-apis`
2. Navigate to: Settings → Secrets and variables → Actions → New repository secret
3. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `APP_ID` | `123456` | Your GitHub App ID (same as destination) |
| `APP_PRIVATE_KEY` | `-----BEGIN RSA PRIVATE KEY-----\n...` | Contents of `.pem` file (same as destination) |

#### B. Copy Notification Workflow

```bash
# Clone or navigate to internal-domo-apis repo
cd /path/to/internal-domo-apis

# Create workflows directory if it doesn't exist
mkdir -p .github/workflows

# Copy the notification workflow from this repo
cp /path/to/documentation-generator-action/.github/workflows/source-repo-notify.yml \
   .github/workflows/notify-doc-sync.yml

# Verify the file
cat .github/workflows/notify-doc-sync.yml

# Commit and push
git add .github/workflows/notify-doc-sync.yml
git commit -m "feat: add documentation sync notification to domo-developer-portal

Triggers documentation generation in domo-developer-portal when
YAML files change in api-docs/public/"

git push origin main
```

#### C. Verify Deployment

- [ ] Go to Actions tab in `domoinc/internal-domo-apis`
- [ ] Confirm "Notify Documentation Sync" workflow appears
- [ ] Check it's not showing any errors

---

## Testing

### Test 1: Manual Trigger (Safest First Test)

1. Go to `DomoApps/domo-developer-portal` → Actions
2. Select "Sync API Documentation from Source Repo"
3. Click "Run workflow"
4. Select branch: `main`
5. Check "Force regenerate all docs": `false` (test change detection)
6. Click "Run workflow"

**What to expect:**
- Workflow starts running
- Steps complete: Clone, Detect, Generate (if changes), Sync, PR
- If no changes: Workflow completes with "No changes detected"
- If changes: PR created with updated docs

### Test 2: End-to-End Test

1. In `domoinc/internal-domo-apis`, make a test change:
   ```bash
   cd /path/to/internal-domo-apis

   # Make a small change to trigger sync
   echo "# Test change - $(date)" >> api-docs/public/AI-Services.yaml

   git add api-docs/public/AI-Services.yaml
   git commit -m "test: trigger documentation sync"
   git push origin main
   ```

2. **Monitor Source Repo:**
   - Go to Actions in `internal-domo-apis`
   - Watch "Notify Documentation Sync" workflow
   - Should complete in < 30 seconds
   - Check it says "Notification Sent"

3. **Monitor Destination Repo:**
   - Go to Actions in `domo-developer-portal`
   - Watch "Sync API Documentation from Source Repo" workflow
   - Should start within 30 seconds of source notification
   - Expected duration: 5-10 minutes

4. **Check Pull Request:**
   - Go to Pull Requests in `domo-developer-portal`
   - Should see new PR with title "📚 Sync API Documentation..."
   - Review the PR:
     - [ ] Changed files look correct
     - [ ] Documentation quality is acceptable
     - [ ] Mapping config updated correctly (if new files)
   - Merge the PR

### Test 3: New File Test

1. Add a new YAML file to source repo:
   ```bash
   cp api-docs/public/AI-Services.yaml api-docs/public/New-API.yaml
   # Edit New-API.yaml to be different

   git add api-docs/public/New-API.yaml
   git commit -m "test: add new API file"
   git push origin main
   ```

2. Wait for workflows to complete

3. Check PR includes:
   - [ ] New markdown file: `docs/API-Reference/Product-APIs/New-API.md`
   - [ ] Updated mapping: `.github/doc-mapping.json` has new entry
   - [ ] PR description mentions "New Files (1)"

---

## Troubleshooting

### Issue: "Source repo clone failed"

**Cause**: GitHub App token generation failed or doesn't have access

**Fix:**
1. Verify `APP_ID` is correct
2. Verify `APP_PRIVATE_KEY` includes BEGIN/END lines
3. Verify GitHub App is installed on `domoinc/internal-domo-apis`
4. Check App has "Contents: Read" permission
5. Re-generate private key if needed

### Issue: "Notification workflow failed in source repo"

**Cause**: GitHub App can't trigger destination workflow

**Fix:**
1. Verify GitHub App is installed on `DomoApps/domo-developer-portal`
2. Check App has "Workflows: Write" permission
3. Verify `APP_ID` and `APP_PRIVATE_KEY` in source repo secrets
4. Check token generation step in workflow logs

### Issue: "OpenAI API error"

**Cause**: Invalid API key or rate limit

**Fix:**
1. Verify API key is correct
2. Check OpenAI dashboard for usage/errors
3. Ensure billing is set up on OpenAI account

### Issue: "No changes detected" when there should be changes

**Cause**: File modification times or path issues

**Fix:**
1. Run with "Force regenerate all docs" option
2. Check paths in `.github/doc-mapping.json`
3. Verify `source_base` and `dest_base` are correct

### Issue: "Files generated in wrong location"

**Cause**: Incorrect mapping configuration

**Fix:**
1. Update `.github/doc-mapping.json` with correct paths
2. Re-run workflow (manual trigger)
3. Manually move/delete files if needed
4. See CROSS_REPO_SYNC.md for mapping examples

---

## Post-Deployment

### Immediate Actions
- [ ] Test manual trigger
- [ ] Test end-to-end with source push
- [ ] Test new file detection
- [ ] Document any issues encountered
- [ ] Update team on new workflow

### First Week
- [ ] Monitor workflow success rate
- [ ] Review generated documentation quality
- [ ] Adjust `MAX_ITERATIONS` or `COMPLETENESS_THRESHOLD` if needed
- [ ] Gather team feedback

### Ongoing Maintenance
- [ ] Weekly: Check for failed workflow runs
- [ ] Monthly: Review and clean up mapping config
- [ ] Monthly: Check OpenAI API usage/costs
- [ ] Quarterly: Rotate PAT tokens

---

## Rollback Plan

If something goes wrong and you need to disable the sync:

### Disable Destination Workflow
1. Go to `DomoApps/domo-developer-portal` → Actions
2. Select "Sync API Documentation from Source Repo"
3. Click "..." → Disable workflow

### Disable Source Notification
1. Go to `domoinc/internal-domo-apis` → Actions
2. Select "Notify Documentation Sync"
3. Click "..." → Disable workflow

OR delete the workflow file:
```bash
cd /path/to/internal-domo-apis
git rm .github/workflows/notify-doc-sync.yml
git commit -m "temp: disable doc sync notification"
git push
```

---

## Success Criteria

The deployment is successful when:

✅ Both workflows appear in Actions tabs
✅ Manual trigger completes successfully
✅ Source push triggers destination workflow
✅ PR is created with generated documentation
✅ Documentation quality meets standards (90%+ scores)
✅ Files land in correct locations
✅ New files are auto-mapped correctly

---

## Questions or Issues?

- Check detailed logs in Actions workflow runs
- Review `CROSS_REPO_SYNC.md` for full documentation
- Test locally using Python scripts if needed
- Reach out to team if stuck
