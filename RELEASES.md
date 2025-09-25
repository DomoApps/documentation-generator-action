# Releases & Versioning

This document outlines the release process and versioning strategy for the YAML to Markdown Documentation Generator.

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backwards compatible)
- **PATCH** version: Bug fixes (backwards compatible)

## Release Process

### 1. Create a Release

1. **Test thoroughly** on a sample repository
2. **Update CHANGELOG.md** with new features and fixes
3. **Create a GitHub Release** with proper tag

### 2. Tagging Strategy

- **Latest stable**: `v1`, `v1.2`, `v1.2.3`
- **Pre-release**: `v1.2.3-beta.1`, `v1.2.3-alpha.1`
- **Development**: `main` branch

### 3. Release Commands

```bash
# Create and push a new tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial stable release"
git push origin v1.0.0

# Update major version tag
git tag -fa v1 -m "Update v1 to latest stable"
git push origin v1 --force
```

## Usage Examples by Version

### Latest Stable (Recommended)
```yaml
- uses: your-org/yaml-to-docs-action@v1
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Specific Version (Production)
```yaml
- uses: your-org/yaml-to-docs-action@v1.2.3
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Development Version (Testing)
```yaml
- uses: your-org/yaml-to-docs-action@main
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## Version History

### v1.0.0 (Initial Release)
- ✅ YAML to Markdown conversion with AI
- ✅ Template-based documentation generation
- ✅ Iterative refinement with exit conditions
- ✅ Composite action support
- ✅ Reusable workflow support
- ✅ Comprehensive error handling
- ✅ GitHub Actions integration

## Breaking Changes

### v1.0.0
- Initial release - no breaking changes

---

## Release Checklist

Before creating a new release:

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version tested on sample repository
- [ ] GitHub Release created with notes
- [ ] Tags pushed to repository
- [ ] Major version tag updated (if applicable)