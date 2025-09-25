# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial YAML to Markdown documentation generator
- AI-powered iterative refinement process
- Template-based documentation generation
- Composite GitHub Action support
- Reusable workflow support
- Comprehensive error handling and validation
- Support for OpenAPI 3.x specifications
- Configurable AI models (GPT-4o, GPT-4, GPT-3.5)
- Quality scoring and exit conditions
- Batch processing of multiple YAML files

### Changed
- Transformed from PR review action to documentation generator
- Updated from ChatGPT-specific to general OpenAI API usage
- Migrated from GitHub API integration to file-based processing

### Removed
- GitHub PR review functionality
- Git diff analysis
- Line comment generation
- Repository integration features

## [1.0.0] - TBD

### Added
- 🚀 **Initial Release** of YAML to Markdown Documentation Generator
- 🤖 **AI-Powered Generation** with iterative refinement
- 📄 **Template System** using Handlebars-style placeholders
- ⚙️ **Configurable Processing** with multiple parameters
- 📊 **Quality Validation** with scoring and exit conditions
- 🔄 **Batch Processing** for multiple YAML files
- 🎯 **GitHub Actions Integration** with composite action
- 📚 **Comprehensive Documentation** and examples

### Features
- **Input Formats**: YAML, YML files
- **Output Formats**: Markdown with professional formatting
- **AI Models**: GPT-4o (default), GPT-4, GPT-3.5-turbo
- **Templates**: Customizable Handlebars templates
- **Processing**: Up to 10 refinement iterations
- **Quality Control**: 90% completeness threshold (configurable)
- **Error Handling**: Comprehensive validation and error reporting

---

## Version Tags

- `v1` - Latest stable version
- `v1.0` - Latest 1.0.x version
- `v1.0.0` - Specific release version
- `main` - Development branch