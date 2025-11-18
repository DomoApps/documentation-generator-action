# Quick Start Guide - Cross-Repo Documentation Sync

**Goal:** Automatically sync API documentation from `domoinc/internal-domo-apis` to `DomoApps/domo-developer-portal`

**Time to complete:** ~30-45 minutes (one-time setup)

---

## Step-by-Step Instructions

### Phase 1: Create GitHub App (15 minutes)

**📖 Full Guide:** [`.github/GITHUB_APP_SETUP.md`](.github/GITHUB_APP_SETUP.md)

**Quick steps:**

1. **Create the App**
   - Go to: https://github.com/organizations/DomoApps/settings/apps/new
   - Name: `DomoApps Documentation Sync`
   - Homepage: `https://github.com/DomoApps/domo-developer-portal`
   - Uncheck "Webhook Active"

2. **Set Permissions**
   - Contents: **Read and write**
   - Workflows: **Read and write**
   - Pull requests: **Read and write**
   - Metadata: **Read-only** (automatic)

3. **Create App**
   - Click "Create GitHub App"
   - **Save the App ID** (e.g., `123456`)

4. **Generate Private Key**
   - Scroll to "Private keys" section
   - Click "Generate a private key"
   - **Save the `.pem` file securely**

5. **Install on Repositories**
   - Click "Install App" (left sidebar)
   - Select: "Only select repositories"
   - Add: `DomoApps/domo-developer-portal`
   - Add: `domoinc/internal-domo-apis`
   - Click "Install"

---

### Phase 2: Add Secrets to Destination Repo (5 minutes)

Go to: https://github.com/DomoApps/domo-developer-portal/settings/secrets/actions/new

**Add 3 secrets:**

| Name | Value | How to get it |
|------|-------|---------------|
| `APP_ID` | `123456` | From GitHub App settings page |
| `APP_PRIVATE_KEY` | `-----BEGIN RSA PRIVATE KEY-----`<br>`...`<br>`-----END RSA PRIVATE KEY-----` | Open `.pem` file, copy entire contents |
| `OPENAI_API_KEY` | `sk-...` | From https://platform.openai.com/api-keys |

**✅ Checkpoint:** All 3 secrets added to `domo-developer-portal`

---

### Phase 3: Deploy to Destination Repo (5 minutes)

```bash
# In this repo (documentation-generator-action)
git status  # Review changes

# Commit everything
git add .github/ CROSS_REPO_SYNC.md QUICK_START.md README.md
git commit -m "feat: add cross-repo sync with GitHub App authentication"
git push origin main
```

**✅ Checkpoint:**
- Go to Actions tab
- See "Sync API Documentation from Source Repo" workflow

---

### Phase 4: Add Secrets to Source Repo (5 minutes)

Go to: https://github.com/domoinc/internal-domo-apis/settings/secrets/actions/new

**Add 2 secrets:**

| Name | Value |
|------|-------|
| `APP_ID` | `123456` (same as destination) |
| `APP_PRIVATE_KEY` | `-----BEGIN RSA...` (same as destination) |

**✅ Checkpoint:** Both secrets added to `internal-domo-apis`

---

### Phase 5: Deploy to Source Repo (5 minutes)

```bash
# Clone or navigate to internal-domo-apis
cd /path/to/internal-domo-apis

# Create directory
mkdir -p .github/workflows

# Copy notification workflow
cp /path/to/documentation-generator-action/.github/workflows/source-repo-notify.yml \
   .github/workflows/notify-doc-sync.yml

# Commit
git add .github/workflows/notify-doc-sync.yml
git commit -m "feat: add doc sync notification to domo-developer-portal"
git push origin main
```

**✅ Checkpoint:**
- Go to Actions tab
- See "Notify Documentation Sync" workflow

---

### Phase 6: Test (10-15 minutes)

#### Test 1: Manual Trigger

1. Go to: https://github.com/DomoApps/domo-developer-portal/actions
2. Click "Sync API Documentation from Source Repo"
3. Click "Run workflow"
4. Leave "Force regenerate" unchecked
5. Click "Run workflow"
6. Wait 5-10 minutes
7. **Expected:** Either "No changes" or PR created

#### Test 2: End-to-End

1. In `internal-domo-apis`, make a test change:
   ```bash
   cd /path/to/internal-domo-apis
   echo "# Test - $(date)" >> api-docs/public/AI-Services.yaml
   git add api-docs/public/AI-Services.yaml
   git commit -m "test: trigger doc sync"
   git push origin main
   ```

2. **Watch source repo Actions** (~30 seconds)
   - "Notify Documentation Sync" should run
   - Should complete successfully

3. **Watch destination repo Actions** (~5-10 minutes)
   - "Sync API Documentation" should start automatically
   - Monitor progress through steps

4. **Check for PR**
   - Go to Pull Requests
   - Should see: "📚 Sync API Documentation..."
   - Review changes
   - **Merge if looks good!**

#### Test 3: New File

1. Add new YAML file:
   ```bash
   cd /path/to/internal-domo-apis
   cp api-docs/public/AI-Services.yaml api-docs/public/Test-API.yaml
   git add api-docs/public/Test-API.yaml
   git commit -m "test: new API file"
   git push
   ```

2. Wait for PR

3. **Verify PR includes:**
   - ✅ New file: `docs/API-Reference/Product-APIs/Test-API.md`
   - ✅ Updated: `.github/doc-mapping.json`
   - ✅ PR mentions "New Files (1)"

**✅ All tests passed!** System is working.

---

## Success Criteria

You're done when:

✅ GitHub App created and installed on both repos
✅ All secrets added to both repos
✅ Workflows deployed to both repos
✅ Manual trigger test passes
✅ End-to-end test creates PR successfully
✅ Generated documentation looks good
✅ New file test auto-maps correctly

---

## Troubleshooting

**Problem:** Workflow fails with "Bad credentials"

**Solution:** Check `APP_ID` and `APP_PRIVATE_KEY` are correct, include BEGIN/END lines

---

**Problem:** "App not installed on repository"

**Solution:** Go to GitHub App settings → Install App → Add missing repo

---

**Problem:** No PR created after source push

**Solution:**
1. Check source repo workflow ran (Actions tab)
2. Check destination repo workflow started
3. Look for errors in workflow logs

---

**Problem:** Documentation quality is poor

**Solution:**
1. Check OpenAI API key is valid
2. Review source YAML completeness
3. Adjust quality thresholds in workflow if needed

---

## What Happens After Setup?

**Automatic sync:**
- Developer pushes YAML changes → Destination gets notified → Docs generated → PR created
- **Every 6 hours** as backup check
- **No manual work needed!**

**When PR is created:**
1. Review generated documentation
2. Check mapping config (if new files)
3. Merge when satisfied

**Maintenance:**
- None! Tokens auto-rotate
- Optionally review every quarter

---

## Documentation Reference

**For you (now):**
- This file - Quick start
- `.github/DEPLOYMENT_CHECKLIST.md` - Detailed steps
- `.github/GITHUB_APP_SETUP.md` - GitHub App guide

**For ongoing use:**
- `CROSS_REPO_SYNC.md` - How it works, advanced config
- `.github/CROSS_REPO_SETUP_SUMMARY.md` - Quick reference

**For troubleshooting:**
- Workflow logs in Actions tab
- `CROSS_REPO_SYNC.md` - Troubleshooting section
- `.github/DEPLOYMENT_CHECKLIST.md` - Common issues

---

## Next Steps

1. ⬜ Create GitHub App (Phase 1)
2. ⬜ Add secrets to destination (Phase 2)
3. ⬜ Deploy to destination (Phase 3)
4. ⬜ Add secrets to source (Phase 4)
5. ⬜ Deploy to source (Phase 5)
6. ⬜ Run tests (Phase 6)
7. ⬜ Celebrate! 🎉

---

**Questions?** Check the detailed guides or workflow logs for more info.

**Ready to start?** Begin with Phase 1: Create GitHub App
