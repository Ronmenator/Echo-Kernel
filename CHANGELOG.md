# Changelog

All notable changes to EchoKernel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release
- Core EchoKernel framework with provider system
- Tool integration capabilities
- Advanced agent system with multiple agent types
- Vector memory and storage support
- Code interpreter tool with sandboxed execution
- Comprehensive documentation and examples

### Features
- **EchoKernel**: Central hub for managing AI providers and tools
- **Provider System**: Support for Azure OpenAI and OpenAI providers
- **Tool System**: Decorator-based tool creation and registration
- **Agent System**: 
  - EchoAgent: Basic agent with persona and tools
  - TaskDecomposerAgent: Breaks complex tasks into subtasks
  - LoopAgent: Iteratively improves results
  - RouterAgent: Routes tasks to specialist agents
  - SpecialistRouterAgent: Enhanced router with retry logic
  - MemoryAgent: Maintains context across conversations
- **Vector Memory**: Semantic search and storage capabilities
- **Code Interpreter**: Safe Python code execution in sandboxed environment

### Technical Details
- Async/await support throughout the framework
- Type hints for all public APIs
- Modular architecture for easy extension
- Cross-platform compatibility (Windows, Linux, macOS)
- Resource limits and safety measures for code execution

## [0.1.1] - 2025-06-02

### Added
- **PyPI Package Distribution**: Full packaging setup for pip installation
- **Command-Line Interface**: `echo-kernel` CLI tool for interactive and single-query usage
- **Modern Packaging Configuration**: `pyproject.toml` with PEP 621 compliance
- **Automated Build System**: `build_package.py` script for streamlined package building
- **GitHub Actions Workflow**: Automated releases to PyPI on version tags
- **Comprehensive Documentation**: 
  - `PACKAGING.md`: Complete packaging and distribution guide
  - `RELEASE_CHECKLIST.md`: Step-by-step release process
  - Updated `README.md` with pip installation instructions
- **Development Tools Integration**: Black, mypy, and pytest configuration
- **Package Metadata**: Proper classifiers, keywords, and project URLs

### Changed
- **Updated `setup.py`**: Minimal version for backward compatibility
- **Enhanced `MANIFEST.in`**: Proper file inclusion/exclusion for distribution
- **License Configuration**: Modern SPDX license format in `pyproject.toml`
- **Dependencies Management**: Organized into core and optional development dependencies

### Technical Improvements
- **CLI Features**:
  - Interactive mode with help system
  - Single query mode for automation
  - Provider selection (Azure OpenAI/OpenAI)
  - Model override capabilities
  - Environment variable configuration
- **Build System**:
  - Automated dependency installation
  - Package validation with twine
  - Clean build artifact management
  - Support for both source and wheel distributions
- **CI/CD Pipeline**:
  - Automated package building on tag push
  - PyPI upload with API token authentication
  - GitHub release creation
  - Package validation checks

### Installation Options
- **PyPI Installation**: `pip install echo-kernel`
- **Development Installation**: `pip install -e .`
- **Development Dependencies**: `pip install echo-kernel[dev]`
- **CLI Usage**: `echo-kernel --interactive` or `echo-kernel "query"`

### Files Added
- `pyproject.toml` - Main package configuration
- `echo_kernel/cli.py` - Command-line interface
- `build_package.py` - Build automation script
- `.github/workflows/release.yml` - Automated release workflow
- `PACKAGING.md` - Packaging documentation
- `RELEASE_CHECKLIST.md` - Release process guide
- `MANIFEST.in` - Package file inclusion rules

### Files Modified
- `setup.py` - Simplified for backward compatibility
- `README.md` - Added pip installation instructions and CLI usage

## [0.1.0] - 2025-06-19

### Added
- Initial release of EchoKernel framework
- Basic provider system for AI services
- Tool integration framework
- Agent system with multiple agent types
- Vector memory and storage support
- Code interpreter with safety features
- Comprehensive documentation and examples

### Dependencies
- openai>=1.0.0
- numpy>=1.21.0
- qdrant-client>=1.7.0
- faiss-cpu>=1.7.0
- python-dotenv>=1.0.0
- requests>=2.25.0
- typing-extensions>=4.0.0

---

## Version History

### Version 0.1.1
- **Release Date**: 2025-06-02
- **Status**: Packaging and distribution improvements
- **Key Features**: PyPI distribution, CLI tool, automated releases
- **Breaking Changes**: None

### Version 0.1.0
- **Release Date**: 2024-01-XX
- **Status**: Initial public release
- **Key Features**: Core framework, agent system, tool integration, vector memory
- **Breaking Changes**: None (initial release)

---

## Contributing to Changelog

When adding entries to the changelog, please follow these guidelines:

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

### Format
- Use clear, concise descriptions
- Include issue numbers when applicable
- Group related changes together
- Use present tense ("Add feature" not "Added feature")

### Example
```markdown
## [1.2.0] - 2025-XX-XX

### Added
- New feature for enhanced agent routing (#123)
- Support for additional AI providers

### Fixed
- Memory leak in vector storage (#124)
- Incorrect error handling in tool execution

### Changed
- Updated minimum Python version to 3.8
- Improved error messages for better debugging
``` 