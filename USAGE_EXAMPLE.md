# Using the Documentation Generator Action

This example shows how to use the `DomoApps/documentation-generator-action` from another repository.

## Repository Structure (Your API Repo)


```text
your-api-repository/
├── .github/workflows/
│   └── generate-docs.yml          # ← This workflow file
├── yaml/                          # ← Your YAML files
│   ├── user-api.yaml
│   ├── payment-api.yaml
│   └── orders-api.yaml
├── templates/                     # ← Optional custom templates
│   └── custom-template.md
└── docs/                          # ← Generated documentation (auto-created)
    ├── user-api.md
    ├── payment-api.md
    └── orders-api.md
```

## Workflow File: `.github/workflows/generate-docs.yml`

```yaml
name: Generate API Documentation

on:
  push:
    paths:
      - 'yaml/**/*.yaml'
      - 'yaml/**/*.yml'
  pull_request:
    paths:
      - 'yaml/**/*.yaml'
      - 'yaml/**/*.yml'
  workflow_dispatch: # Manual trigger

jobs:
  generate_docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - name: Generate API Documentation
        uses: DomoApps/documentation-generator-action@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          yaml_input_path: './yaml'
          output_path: './docs'
          template_path: 'default'  # Uses action's built-in template
          openai_model: 'gpt-4o'
          max_iterations: '5'
          completeness_threshold: '90'
          timeout_minutes: '10'

      - name: Commit Generated Documentation
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "Documentation Bot"
          git add docs/
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "📚 Update API documentation from YAML changes"
            git push
          fi
```

## Alternative: Create Pull Request Instead

```yaml
      - name: Create Pull Request with Documentation
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: '📚 Update API documentation'
          title: '📚 Auto-generated Documentation Update'
          body: |
            ## 🤖 Documentation Update

            This PR contains automatically generated documentation from YAML file changes.

            Please review before merging.
          branch: docs/auto-update
          delete-branch: true
          add-paths: |
            docs/**
```


## Required Setup in Your API Repository

### 1. Add Repository Secret

Go to your repository → Settings → Secrets and variables → Actions

Add: `OPENAI_API_KEY` with your OpenAI API key

### 2. Directory Structure

Create these directories in your repository:

```bash
mkdir -p yaml docs
```

### 3. Sample YAML File

Create `yaml/sample-api.yaml`:
```yaml
openapi: 3.0.0
info:
  title: Sample API
  description: A sample API for testing documentation generation
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get all users
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
```

## Using Custom Templates

If you want to use your own template instead of the default:

1. Create `templates/my-custom-template.md` in your repo
2. Update the workflow:
```yaml
      - name: Generate API Documentation
        uses: DomoApps/documentation-generator-action@main
        with:
          # ... other inputs ...
          template_path: './templates/my-custom-template.md'
```


## Expected Behavior

1. **On YAML file changes**: Action generates new documentation
2. **Generated files**: Placed in `./docs/` directory
3. **Automatic commit**: Documentation is committed back to the repo
4. **File naming**: YAML files become markdown (e.g., `user-api.yaml` → `user-api.md`)

## ⚠️ Common Issues

- **Case Sensitivity**: Must use `DomoApps/documentation-generator-action` (not `domoapps`)
- **Repository Access**: Ensure your repo can access the DomoApps organization
- **API Key**: Verify `OPENAI_API_KEY` is set in repository secrets

## Testing

To test manually:
1. Push a YAML file to the `yaml/` directory
2. Check the Actions tab for the workflow run
3. Generated documentation will appear in `docs/` directory
