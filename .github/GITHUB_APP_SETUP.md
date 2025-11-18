# GitHub App Setup Guide

This guide walks you through creating and configuring a GitHub App for secure cross-repository documentation synchronization.

## Why GitHub App Instead of PAT?

✅ **Organization-owned** - Not tied to individual users.

✅ **Fine-grained permissions** - Only access what's needed.

✅ **Automatic token generation** - No manual rotation.

✅ **Better security** - Short-lived tokens, auto-renewed.

✅ **Audit trail** - Actions show as "App" not user.

✅ **Professional** - Industry best practice.

## Part 1: Create the GitHub App

### Important Context

**What we're creating:** A GitHub App that acts as an authentication mechanism for workflows
**What we're NOT creating:** A publicly installable app or webhook receiver
**Why it's simple:** We only need the App to generate tokens for API calls

### Step 1: Navigate to GitHub App Creation

**For Organization:**

1. Go to your organization: `https://github.com/organizations/DomoApps/settings/apps`
2. Click "New GitHub App" button (top right)

**OR use direct link:**

```
https://github.com/organizations/DomoApps/settings/apps/new
```

**Recommended:** Create in the organization that owns the destination repo (`DomoApps`)

### Step 2: Configure Basic Information

**GitHub App name:**

```
DomoApps Documentation Sync
```

**Homepage URL:**

```
https://github.com/DomoApps/domo-developer-portal
```

**Description:**

```
Automatically syncs API documentation from internal-domo-apis to domo-developer-portal
```

**Callback URL:**

- Leave blank (not needed - we're only using this for API authentication, not OAuth)

**Request user authorization (OAuth) during installation:**

- ⬜ Uncheck this (we don't need OAuth)

**Webhook:**

- ⬜ **Uncheck "Active"** ⚠️ IMPORTANT
- We don't need webhooks - our workflows will use the App just for authentication
- Leave "Webhook URL" blank

**Webhook secret (optional):**

- Leave blank (not using webhooks)

### Step 3: Configure Permissions

#### Repository Permissions

Set these permissions:

| Permission        | Access Level   | Reason                                             |
| ----------------- | -------------- | -------------------------------------------------- |
| **Contents**      | Read and write | Clone repos, read YAML files, write markdown files |
| **Metadata**      | Read-only      | (automatically set)                                |
| **Pull requests** | Read and write | Create PRs with generated documentation            |
| **Workflows**     | Read and write | Trigger workflows via repository_dispatch          |

#### Organization Permissions

- None needed

#### Account Permissions

- None needed

### Step 4: Where can this GitHub App be installed?

Select: **Only on this account**

This restricts the app to your organization's repositories only.

### Step 5: Review & Create

**Before clicking "Create GitHub App", verify:**

✅ Webhook is **unchecked** (Active: No)

✅ Contents permission: **Read and write**

✅ Workflows permission: **Read and write**

✅ Pull requests permission: **Read and write**

✅ "Where can this GitHub App be installed?" is set to **Only on this account**

**Then:**

1. Scroll to bottom
2. Click **Create GitHub App**
3. You'll be redirected to the app's settings page

**✅ Checkpoint:** You should now see your app's settings page with an App ID at the top

---

## Part 2: Generate and Save Private Key

### Step 1: Generate Private Key

1. On the app settings page, scroll down to **Private keys**
2. Click **Generate a private key**
3. A `.pem` file will download automatically
4. **IMPORTANT:** Save this file securely - you can't download it again!

**File name:** `DomoApps-Documentation-Sync.YYYY-MM-DD.private-key.pem`

### Step 2: Note the App ID

At the top of the app settings page, note:

- **App ID**: `123456` (you'll need this)
- **Client ID**: (not needed for our use case)

---

## Part 3: Install the App on Repositories

### Step 1: Install on Destination Repo

1. On the app settings page, click **Install App** (left sidebar)
2. Select your organization
3. Choose: **Only select repositories**
4. Select: `DomoApps/domo-developer-portal`
5. Click **Install**

### Step 2: Install on Source Repo (OPTIONAL)

**⚠️ IMPORTANT: Source repo workflow is OPTIONAL!**

The destination repo workflow runs autonomously on a schedule (every 6 hours by default) and doesn't require the source repo to notify it. Installing the app on the source repo enables faster notifications but is not required.

**Skip this step if:**
- You cannot add secrets to the source repository
- Scheduled polling (every 6 hours) is sufficient for your use case
- You prefer manual triggers using workflow_dispatch

**Only proceed with source repo setup if:**
- You want real-time notifications when source YAML files change
- You have permission to add secrets to the source repository
- You want to reduce the delay between source changes and doc updates

---

**Option A: Same Organization**
If source repo is in same org, just add it:

1. Go back to Install App
2. Click the gear icon next to your installation
3. Add repository: `domoinc/internal-domo-apis`
4. Click **Save**

**Note:** The App will have the same permissions on source repo as destination. This is fine and safe - the source workflow only uses the "trigger workflow" capability (repository_dispatch).

**Option B: Different Organization**
If source is in a different org (`domoinc`):

1. Repeat the installation process in that organization
2. Select only `domoinc/internal-domo-apis`

**Alternative for Different Org:** If you want minimal permissions on source:

- Create a **second GitHub App** in `domoinc` org
- Give it only: **Workflows: Read and write** (to send repository_dispatch)
- Install only on `internal-domo-apis`
- Use different `APP_ID` and `APP_PRIVATE_KEY` in source repo secrets

**If you skip source repo setup:** The destination workflow will still work perfectly using scheduled triggers. See "Running Without Source Repo Secrets" section below.

---

## Part 4: Configure GitHub Secrets

### For Destination Repo (`DomoApps/domo-developer-portal`)

Go to: Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

#### 1. `APP_ID`

```
Value: 123456  (your actual App ID)
```

#### 2. `APP_PRIVATE_KEY`

```
Value: (paste entire contents of the .pem file)

Should look like:
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(many lines)
...
-----END RSA PRIVATE KEY-----
```

**Important:** Include the BEGIN and END lines!

#### 3. `OPENAI_API_KEY`

```
Value: sk-...
```

### For Source Repo (`domoinc/internal-domo-apis`) - OPTIONAL

**⚠️ Only needed if you want real-time notifications from source repo!**

If you cannot add secrets to the source repo (e.g., organization restrictions), skip this section. The destination workflow will run on a schedule instead.

If you want to set up source repo notifications, add these secrets:

#### 1. `APP_ID`

```
Value: 123456  (same App ID)
```

#### 2. `APP_PRIVATE_KEY`

```
Value: (same .pem file contents)
```

---

## Part 4.5: Running Without Source Repo Secrets

If you cannot add secrets to the source repository, you can still use this system! The destination repo workflow is designed to work autonomously.

### How It Works

The destination repo (`DomoApps/domo-developer-portal`) workflow:

1. **Runs on a schedule** (every 6 hours by default)
2. **Clones the source repo** using the GitHub App token (stored in destination repo)
3. **Detects changes** by comparing source YAML file timestamps with destination markdown files
4. **Generates documentation** for changed files only
5. **Creates a PR** with the updates

### No Source Repo Configuration Needed

- ✅ Source repo requires **zero secrets**
- ✅ Source repo requires **zero workflow files**
- ✅ Source repo requires **zero configuration**

The destination repo does all the work!

### Triggering Options

**1. Automatic (Scheduled)**
- Runs every 6 hours automatically
- No action needed
- Change detection happens automatically

**2. Manual (On-Demand)**
- Go to destination repo: Actions → "Sync API Documentation" workflow
- Click "Run workflow"
- Optional: Check "Force regenerate all docs" to rebuild everything

**3. Adjust Schedule (Optional)**
Edit `.github/workflows/sync-api-docs.yml` in destination repo:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours (current)
  # Examples:
  # - cron: '0 * * * *'    # Every hour
  # - cron: '*/30 * * * *' # Every 30 minutes
  # - cron: '0 0 * * *'    # Once per day at midnight
```

### Advantages of This Approach

- ✅ Works even if source repo has strict permission policies
- ✅ All secrets in one place (destination repo)
- ✅ Easier to manage and troubleshoot
- ✅ More secure (fewer places to store secrets)

### Disadvantages

- ⚠️ Not real-time (max 6 hour delay with default schedule)
- ⚠️ Uses more Actions minutes (clones source repo every run)

For most use cases, a 6-hour sync delay is perfectly acceptable for documentation updates.

---

## Part 5: Update Workflow Files (Optional - Source Repo Only)

**⚠️ Skip this entire section if you're not setting up source repo notifications!**

This section only applies if you want the source repo to send real-time notifications to the destination repo. If you're using scheduled polling (recommended if you can't add secrets to source repo), skip to Part 6.

The workflow files need to be updated to use GitHub App authentication instead of PATs.

### Key Changes

**Before (PAT):**

```yaml
- uses: actions/checkout@v4
  with:
    repository: domoinc/internal-domo-apis
    token: ${{ secrets.SOURCE_REPO_PAT }} # User token
```

**After (GitHub App):**

```yaml
- uses: actions/create-github-app-token@v1
  id: app-token
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
    owner: domoinc
    repositories: internal-domo-apis

- uses: actions/checkout@v4
  with:
    repository: domoinc/internal-domo-apis
    token: ${{ steps.app-token.outputs.token }} # App token
```

**Benefits:**

- Token is generated on-the-fly
- Token expires after job completes
- No manual rotation needed
- More secure

---

## Part 6: Testing the GitHub App

### Test 1: Verify App Installation

1. Go to each repo → Settings → GitHub Apps
2. Verify "DomoApps Documentation Sync" is installed
3. Check it has the correct permissions

### Test 2: Test Token Generation

Run this workflow to verify token generation works:

```yaml
name: Test GitHub App
on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Generate token
        uses: actions/create-github-app-token@v1
        id: app-token
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}

      - name: Use token
        run: |
          echo "Token generated successfully"
          # Test API call
          curl -H "Authorization: Bearer ${{ steps.app-token.outputs.token }}" \
               https://api.github.com/user
```

### Test 3: Run Full Sync

Follow the same testing steps from `DEPLOYMENT_CHECKLIST.md`:

1. Manual trigger
2. End-to-end test with source push
3. New file test

---

## Security Best Practices

### Storing the Private Key

✅ **DO:**

- Store `.pem` file in secure password manager
- Encrypt the file if storing locally
- Limit access to team members who need it
- Keep backup in secure location

❌ **DON'T:**

- Commit `.pem` file to git
- Share via email/Slack
- Store in plain text
- Give everyone access

### Rotating Keys

GitHub Apps support multiple private keys, so you can rotate without downtime:

1. Generate new private key
2. Update secrets in both repos
3. Test with new key
4. Delete old private key from GitHub

Recommended rotation: Every 90 days

### Monitoring

Check App activity:

1. Go to App settings
2. Click "Advanced" tab
3. View recent deliveries and errors
4. Monitor for suspicious activity

---

## Troubleshooting

### Error: "Resource not accessible by integration"

**Cause:** App doesn't have required permissions

**Fix:**

1. Go to App settings
2. Check repository permissions
3. Ensure Contents, Workflows, and Pull Requests are set correctly
4. Reinstall app if needed

### Error: "Bad credentials"

**Cause:** Private key or App ID is incorrect

**Fix:**

1. Verify `APP_ID` matches the ID in app settings
2. Verify `APP_PRIVATE_KEY` includes BEGIN/END lines
3. Check for extra spaces or newlines
4. Re-copy the private key contents

### Error: "App not installed on repository"

**Cause:** App isn't installed on the repo you're trying to access

**Fix:**

1. Go to app's Install App page
2. Add the missing repository
3. Save changes

### Token Generation Fails

**Cause:** The `actions/create-github-app-token` action may need updating

**Fix:**
Update to latest version:

```yaml
- uses: actions/create-github-app-token@v1 # Check for newer version
```

---

## Comparison: PAT vs GitHub App

| Feature          | PAT                   | GitHub App            |
| ---------------- | --------------------- | --------------------- |
| Setup time       | 2 minutes             | 15-20 minutes         |
| Security         | User-level access     | Fine-grained per repo |
| Ownership        | Individual user       | Organization          |
| Token lifetime   | Until revoked/expired | Per job (~1 hour)     |
| Rotation         | Manual                | Automatic             |
| Audit trail      | Shows as user         | Shows as app          |
| Scalability      | Limited               | Excellent             |
| Production ready | No                    | Yes                   |
| Team friendly    | No                    | Yes                   |

---

## Migration from PAT (If Already Using)

If you already have the system running with PATs:

1. ✅ Keep existing system running
2. ✅ Create GitHub App (this guide)
3. ✅ Add App secrets alongside PAT secrets
4. ✅ Update workflows to use App
5. ✅ Test thoroughly
6. ✅ Once confirmed working, remove PAT secrets
7. ✅ Delete old PATs from GitHub

This allows zero-downtime migration.

---

## Appendix: Complete Form Field Reference

When creating the GitHub App, here's **every field** and what to set:

### Register new GitHub App Form

**Basic Information:**

- ✅ **GitHub App name**: `DomoApps Documentation Sync`
- ✅ **Description**: `Automatically syncs API documentation from internal-domo-apis to domo-developer-portal`
- ✅ **Homepage URL**: `https://github.com/DomoApps/domo-developer-portal`
- ⬜ **Callback URL**: _Leave blank_

**Identify and authorize users:**

- ⬜ **Request user authorization (OAuth) during installation**: _Uncheck_
- ⬜ **Enable Device Flow**: _Leave unchecked_
- ⬜ **Expire user authorization tokens**: _Leave unchecked_
- ⬜ **Request user authorization (OAuth) during installation**: _Uncheck_

**Post installation:**

- ⬜ **Setup URL**: _Leave blank_
- ⬜ **Redirect on update**: _Leave unchecked_

**Webhook:**

- ⬜ **Active**: **UNCHECK THIS** ⚠️
- ⬜ **Webhook URL**: _Leave blank_ (grayed out when Active unchecked)
- ⬜ **Webhook secret**: _Leave blank_

**Repository permissions:**

- ✅ **Contents**: Read and write
- ✅ **Pull requests**: Read and write
- ✅ **Workflows**: Read and write
- ⬜ **Metadata**: Read-only (automatic, can't change)
- ⬜ All others: No access

**Organization permissions:**

- ⬜ All: No access (leave at default)

**Account permissions:**

- ⬜ All: No access (leave at default)

**Subscribe to events:**

- ⬜ Don't check any boxes (webhook is not active)

**Where can this GitHub App be installed?**

- 🔘 **Only on this account** (select this)

Then click: **Create GitHub App**

---

## Additional Resources

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Creating a GitHub App](https://docs.github.com/en/apps/creating-github-apps)
- [GitHub App Permissions](https://docs.github.com/en/rest/overview/permissions-required-for-github-apps)
- [actions/create-github-app-token](https://github.com/actions/create-github-app-token)

---

## Support

Questions about GitHub App setup?

- Review this guide
- Check the Complete Form Field Reference (above)
- Check GitHub's official documentation
- Test in a separate test repo first
- Reach out to team if stuck
