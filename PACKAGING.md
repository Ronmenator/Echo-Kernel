# EchoKernel Packaging Guide

This guide explains how to package and distribute EchoKernel as a Python package on PyPI.

## Overview

EchoKernel is now properly configured for distribution via pip. The project uses modern Python packaging standards with `pyproject.toml` as the primary configuration file.

## Package Structure

```
Echo-Py/
├── pyproject.toml          # Main package configuration
├── setup.py               # Backward compatibility (minimal)
├── MANIFEST.in            # Files to include in distribution
├── build_package.py       # Build automation script
├── echo_kernel/           # Main package directory
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   └── ...                # Other modules
├── tools/                 # Additional tools
├── examples/              # Example scripts
└── .github/workflows/     # CI/CD workflows
```

## Quick Start

### 1. Local Development Installation

For development, install the package in editable mode:

```bash
pip install -e .
```

### 2. Build the Package

Use the automated build script:

```bash
python build_package.py --all
```

Or manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*
```

### 3. Test Installation

Test the built package locally:

```bash
pip install dist/echo_kernel-0.1.0.tar.gz
```

## Distribution Options

### 1. TestPyPI (Recommended for Testing)

Upload to TestPyPI first to test the package:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ echo-kernel
```

### 2. PyPI (Production)

Once tested, upload to the main PyPI:

```bash
twine upload dist/*
```

### 3. GitHub Actions (Automated)

The project includes a GitHub Actions workflow that automatically releases to PyPI when you push a tag:

```bash
# Create and push a new version tag
git tag v0.1.0
git push origin v0.1.0
```

## Configuration Files

### pyproject.toml

The main configuration file containing:

- **Project metadata**: name, version, description, authors
- **Dependencies**: required and optional packages
- **Build system**: setuptools configuration
- **Development tools**: black, mypy, pytest settings

### MANIFEST.in

Specifies which files to include in the package distribution:

- README, LICENSE, CHANGELOG
- All Python files in echo_kernel/
- Tools directory
- Excludes build artifacts and development files

### setup.py

Minimal setup.py for backward compatibility. The main configuration is in `pyproject.toml`.

## Version Management

### Semantic Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Updating Version

1. Update version in `pyproject.toml`
2. Update version in `echo_kernel/__init__.py` (if applicable)
3. Update CHANGELOG.md
4. Create and push a new tag

```bash
# Update version in pyproject.toml
# Then create tag
git tag v0.1.1
git push origin v0.1.1
```

## Command-Line Interface

The package includes a CLI tool `echo-kernel` that can be used after installation:

```bash
# Interactive mode
echo-kernel --interactive

# Single query
echo-kernel "Tell me a joke"

# Use specific provider
echo-kernel --provider openai "Hello world"
```

## Development Workflow

### 1. Local Development

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Type checking
mypy echo_kernel/
```

### 2. Testing Package

```bash
# Build package
python build_package.py --build

# Test installation
pip install dist/echo_kernel-*.tar.gz

# Test CLI
echo-kernel --help
```

### 3. Publishing

```bash
# Full build and test process
python build_package.py --all

# Manual upload to TestPyPI
twine upload --repository testpypi dist/*

# After testing, upload to PyPI
twine upload dist/*
```

## PyPI Account Setup

### 1. Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create an account
3. Enable two-factor authentication

### 2. Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new token
3. Copy the token for use in CI/CD

### 3. TestPyPI Account

1. Go to https://test.pypi.org/account/register/
2. Create a separate account for testing
3. Create API token for TestPyPI

## GitHub Actions Setup

### 1. Repository Secrets

Add these secrets to your GitHub repository:

- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your TestPyPI API token (optional)

### 2. Automated Releases

The workflow automatically:

1. Builds the package when you push a tag
2. Runs package checks
3. Uploads to PyPI
4. Creates a GitHub release

## Troubleshooting

### Common Issues

1. **Package not found**: Ensure `echo_kernel/__init__.py` exists
2. **Missing dependencies**: Check `pyproject.toml` dependencies
3. **Build errors**: Clean build artifacts with `python build_package.py --clean`
4. **Upload errors**: Verify PyPI credentials and package name availability

### Package Name Availability

Check if `echo-kernel` is available on PyPI:

```bash
pip search echo-kernel  # Note: pip search is deprecated
# Or check manually at https://pypi.org/project/echo-kernel/
```

If the name is taken, update the name in `pyproject.toml`:

```toml
[project]
name = "echo-kernel-ai"  # or another available name
```

## Best Practices

1. **Always test on TestPyPI first**
2. **Use semantic versioning**
3. **Keep CHANGELOG.md updated**
4. **Test installation in clean environment**
5. **Use GitHub Actions for automated releases**
6. **Include comprehensive documentation**

## Next Steps

After successful packaging:

1. Update README.md with pip installation instructions
2. Add badges for PyPI version, downloads, etc.
3. Set up documentation hosting (Read the Docs)
4. Create release notes for each version
5. Monitor package downloads and issues

## Support

For packaging issues:

1. Check the [Python Packaging User Guide](https://packaging.python.org/)
2. Review [PyPA specifications](https://packaging.python.org/specifications/)
3. Use the build script: `python build_package.py --help` 