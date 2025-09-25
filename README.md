# 🚀 YAML to Markdown Documentation Generator

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A powerful GitHub Action that leverages AI to automatically generate professional Markdown documentation from YAML files. Perfect for API documentation, schema documentation, and configuration guides.

## ✨ Features

- 🤖 **AI-Powered Generation**: Uses OpenAI's GPT models for intelligent content creation
- 📄 **Template-Based**: Handlebars-style templates ensure consistent formatting
- 🔄 **Iterative Refinement**: Multi-pass generation with quality scoring
- 📊 **Quality Control**: Configurable completeness thresholds and validation
- 🚀 **GitHub Actions Ready**: Both composite action and reusable workflow support
- 📚 **Batch Processing**: Handle multiple YAML files simultaneously
- ⚙️ **Highly Configurable**: Customize models, iterations, and output paths

## 🎯 Quick Start

### Option 1: Composite Action (Recommended)

```yaml
name: Generate Documentation
on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate API Documentation
        uses: DomoApps/documentation-generator-action@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          yaml_input_path: './api-specs'
          output_path: './docs'
```

### Option 2: Reusable Workflow

```yaml
name: Generate Documentation
on: [push]

jobs:
  generate_docs:
    uses: DomoApps/documentation-generator-action/.github/workflows/action.yml@main
    with:
      yaml_input_path: './api-specs'
      output_path: './docs'
      openai_model: 'gpt-4o'
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## 📋 Prerequisites

1. **OpenAI API Key**: Add `OPENAI_API_KEY` to your repository secrets
2. **YAML Files**: Place your YAML/YML files in the designated input directory
3. **GitHub Actions**: Ensure Actions are enabled in your repository
4. **Repository Access**: Ensure your repository has access to the `DomoApps` organization

## ⚠️ Important Notes

- **Case Sensitive**: Use exact case `DomoApps/documentation-generator-action` (not `domoapps`)
- **Branch Reference**: Use `@main` branch for latest version

## ⚙️ Configuration Options

| Input                    | Description                                  | Default   | Required |
| ------------------------ | -------------------------------------------- | --------- | -------- |
| `openai_api_key`         | OpenAI API key for AI processing             |           | ✅       |
| `yaml_input_path`        | Path to directory containing YAML files      | `./yaml`  |          |
| `output_path`            | Output directory for generated documentation | `./docs`  |          |
| `template_path`          | Custom template file path                    | `default` |          |
| `openai_model`           | AI model to use                              | `gpt-4o`  |          |
| `max_iterations`         | Maximum refinement iterations                | `10`      |          |
| `completeness_threshold` | Quality score threshold (0-100)              | `90`      |          |
| `timeout_minutes`        | Maximum processing time                      | `30`      |          |

## 🎨 Custom Templates

Create your own Handlebars template for customized output:

```handlebars
# {{API_NAME}}

> {{API_DESCRIPTION}}

## Endpoints

{{#each ENDPOINTS}}
### {{METHOD}} {{PATH}}

{{DESCRIPTION}}

**Parameters:**
{{#each PARAMETERS}}
- `{{name}}` ({{type}}) - {{description}}
{{/each}}
{{/each}}
```

## 💡 Usage Examples

### Basic API Documentation

```yaml
- uses: your-org/yaml-to-docs-action@v1
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    yaml_input_path: './openapi'
    output_path: './api-docs'
```

### Custom Configuration

```yaml
- uses: your-org/yaml-to-docs-action@v1
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    yaml_input_path: './specs'
    output_path: './documentation'
    openai_model: 'gpt-4'
    max_iterations: '15'
    completeness_threshold: '95'
    template_path: './custom-template.md'
```

### Commit Generated Docs Back to Repository

```yaml
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate Documentation
        uses: DomoApps/documentation-generator-action@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}

      - name: Commit Documentation
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git diff --staged --quiet || git commit -m "📚 Update generated documentation"
          git push
```

## Process Overview

The action follows an iterative refinement process:

1. **YAML Analysis**: Parses YAML files and extracts structure, data types, and relationships
2. **Template Population**: Maps YAML data to template placeholders using AI
3. **Documentation Generation**: Creates initial Markdown documentation
4. **Quality Validation**: Scores documentation on completeness, accuracy, and clarity
5. **Refinement Loop**: Iteratively improves documentation until exit conditions are met

### Exit Conditions

The process completes when:

- Overall quality score ≥ completeness threshold (default: 90%)
- All template placeholders are filled
- No critical documentation gaps remain
- Maximum iterations reached (default: 10)

## Template System

The action uses Handlebars-style templates with placeholders like:

- `{{API_NAME}}` - API title
- `{{HTTP_METHOD}}` - Request method
- `{{#each PARAMETERS}}` - Parameter loops
- `{{#if CONDITION}}` - Conditional sections

See `samples/productAPI.template.md` for the complete template structure.

## Outputs

Generated documentation files are saved as GitHub artifacts and can be downloaded from the Actions tab.

## 🏗️ Hosting & Deployment

### Repository Setup

1. **Create a new repository** (recommended name: `documentation-generator-action`)
2. **Copy this codebase** to your new repository
3. **Update references** to point to your organization/repository
4. **Create your first release** with proper versioning

### Release Process

```bash
# Create and push your first release
git tag -a v1.0.0 -m "Release v1.0.0: Initial stable release"
git push origin v1.0.0

# Create major version tag for easy consumption
git tag -a v1 -m "Latest v1.x.x release"
git push origin v1
```

### Repository Structure

```text
DomoApps/documentation-generator-action/
├── .github/workflows/action.yml    # Reusable workflow
├── action.yml                      # Composite action
├── src/                           # Core Python code
├── samples/                       # Example files
├── tests/                        # Test suite
├── README.md                     # This documentation
├── CHANGELOG.md                  # Version history
└── RELEASES.md                   # Release process
```

## 🧪 Testing & Examples

### Local Testing

```bash
# Set environment variables
export OPENAI_API_KEY="your-api-key"
export YAML_INPUT_PATH="./samples"
export MARKDOWN_OUTPUT_PATH="./output"
export TEMPLATE_PATH="./samples/productAPI.template.md"

# Run the generator
python src/doc_generator_main.py
```

### Sample Files Included

- **Input**: `samples/filesets.yaml` - Comprehensive API specification
- **Template**: `samples/productAPI.template.md` - Professional API documentation template
- **Expected Output**: Rich markdown with tables, code examples, and structured sections

## 🚀 Usage in Different Scenarios

### Scenario 1: Separate Repositories

```yaml
# In your API spec repository
name: Generate API Docs
on: [push]
jobs:
  docs:
    uses: DomoApps/documentation-generator-action/.github/workflows/action.yml@main
    with:
      yaml_input_path: './specs'
      output_path: './docs'
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Scenario 2: Monorepo with Multiple APIs

```yaml
# Generate docs for multiple services
name: Generate All Documentation
on: [push]
jobs:
  user-service-docs:
    uses: DomoApps/documentation-generator-action@main
    with:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
      yaml_input_path: './services/user-api'
      output_path: './docs/user-service'

  payment-service-docs:
    uses: DomoApps/documentation-generator-action@main
    with:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
      yaml_input_path: './services/payment-api'
      output_path: './docs/payment-service'
```

### Scenario 3: Documentation Website Integration

```yaml
# Generate docs and deploy to GitHub Pages
name: Update Documentation Site
on: [push]
jobs:
  generate-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate API Documentation
        uses: DomoApps/documentation-generator-action@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          yaml_input_path: './api-specs'
          output_path: './docs-site/content/api'

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs-site
```

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `Unable to resolve action` | Ensure exact case: `DomoApps/documentation-generator-action@main` |
| `Permission denied` | Verify repository access to DomoApps organization |
| `OPENAI_API_KEY not found` | Add API key to repository secrets |
| `No YAML files found` | Check `yaml_input_path` points to directory with .yaml/.yml files |
| `Template not found` | Use `template_path: 'default'` or provide valid custom template path |

### Debug Steps

1. **Check Action Logs**: View detailed logs in GitHub Actions tab
2. **Verify Inputs**: Ensure all required inputs are provided
3. **Test Locally**: Use the local testing commands from the repository
4. **Check Permissions**: Verify workflow has necessary permissions

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Create a branch `<your name>/<feature or bug>` from the `main` branch to ensure your changes are based on the latest code.
2. Make your changes, ensuring they align with the project's coding standards and guidelines.
3. Write clear and concise commit messages to describe your changes.
4. Test your changes thoroughly to ensure they work as expected and do not introduce any new issues.
5. Submit a pull request with a clear and detailed description of your changes, including the problem being solved, the approach taken, and any potential impacts.
6. Engage in the review process by addressing feedback and making necessary updates to your pull request.
