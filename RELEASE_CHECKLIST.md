# EchoKernel Release Checklist

This checklist ensures a smooth release process for EchoKernel packages.

## Pre-Release Checklist

### 1. Code Quality
- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black .`
- [ ] Type checking passes: `mypy echo_kernel/`
- [ ] Linting passes: `flake8 echo_kernel/`
- [ ] No critical bugs in issue tracker

### 2. Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md is updated with new features/fixes
- [ ] All examples work correctly
- [ ] API documentation is current

### 3. Version Management
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `echo_kernel/__init__.py` (if applicable)
- [ ] Update CHANGELOG.md with release notes
- [ ] Commit all changes

### 4. Package Configuration
- [ ] `pyproject.toml` has correct metadata
- [ ] Dependencies are up to date and correct
- [ ] `MANIFEST.in` includes all necessary files
- [ ] `setup.py` is minimal (for backward compatibility)

## Build and Test

### 1. Local Build
```bash
# Clean previous builds
python build_package.py --clean

# Build package
python build_package.py --build

# Check package
python build_package.py --check
```

### 2. Test Installation
```bash
# Install from local build
pip install dist/echo_kernel-*.whl

# Test import
python -c "import echo_kernel; print('Success!')"

# Test CLI
echo-kernel --help
```

### 3. Test in Clean Environment
```bash
# Create new virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install package
pip install dist/echo_kernel-*.whl

# Test functionality
python -c "import echo_kernel; print('Package works!')"
```

## Release Process

### 1. TestPyPI (Recommended First Step)
```bash
# Upload to TestPyPI
python build_package.py --upload-test

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ echo-kernel
```

### 2. PyPI Release
```bash
# Upload to PyPI
python build_package.py --upload
```

### 3. GitHub Release
```bash
# Create and push tag
git tag v0.1.0
git push origin v0.1.0
```

## Post-Release Checklist

### 1. Verification
- [ ] Package appears on PyPI: https://pypi.org/project/echo-kernel/
- [ ] Installation works: `pip install echo-kernel`
- [ ] CLI works: `echo-kernel --help`
- [ ] GitHub release is created automatically

### 2. Documentation Updates
- [ ] Update installation instructions if needed
- [ ] Add any new badges to README.md
- [ ] Update any version-specific documentation

### 3. Monitoring
- [ ] Monitor PyPI download statistics
- [ ] Check for any installation issues
- [ ] Monitor GitHub issues for problems
- [ ] Update dependencies if security issues arise

## Automated Release (GitHub Actions)

The project includes automated releases via GitHub Actions:

1. **Trigger**: Push a tag starting with 'v' (e.g., `v0.1.0`)
2. **Process**:
   - Builds the package
   - Runs package checks
   - Uploads to PyPI
   - Creates GitHub release

### Setup Required
- `PYPI_API_TOKEN` secret in GitHub repository
- PyPI account with API token

## Troubleshooting

### Common Issues

1. **Build fails**: Check `pyproject.toml` syntax
2. **Import errors**: Verify `__init__.py` exports
3. **CLI not found**: Check `project.scripts` in `pyproject.toml`
4. **Upload fails**: Verify PyPI credentials and package name availability

### Package Name Conflicts

If `echo-kernel` is taken on PyPI:
1. Check availability: https://pypi.org/project/echo-kernel/
2. Update name in `pyproject.toml`
3. Update all documentation references

## Version Strategy

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Update Process
1. Determine version bump type
2. Update version in `pyproject.toml`
3. Update CHANGELOG.md
4. Create and push tag
5. Monitor release

## Security Considerations

- [ ] No sensitive data in package
- [ ] Dependencies are up to date
- [ ] No hardcoded API keys
- [ ] Environment variables used for configuration

## Support

For release issues:
1. Check [Python Packaging User Guide](https://packaging.python.org/)
2. Review [PyPA specifications](https://packaging.python.org/specifications/)
3. Use build script: `python build_package.py --help`
4. Check GitHub Actions logs for automated releases 