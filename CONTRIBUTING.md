# Contributing to EchoKernel

Thank you for your interest in contributing to EchoKernel! This document provides guidelines and information for contributors.

## 🎯 Project Goals

EchoKernel aims to be:
- **Simple**: Easy to use and understand
- **Flexible**: Support multiple AI providers and use cases
- **Extensible**: Easy to add new providers, tools, and agents
- **Well-documented**: Clear documentation and examples
- **Production-ready**: Reliable and performant

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic understanding of async/await in Python

### Development Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/Echo-Py.git
   cd Echo-Py
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install in development mode:
   ```bash
   pip install -e .
   ```
5. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📝 Code Style Guidelines

### Python Code
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for all function parameters and return values
- Keep functions focused and single-purpose
- Use meaningful variable and function names

### Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings where appropriate
- Update README.md for user-facing changes

### Example Docstring Format
```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of what the function does.
    
    Longer description if needed, explaining the function's purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.
    
    Returns:
        Description of what the function returns.
    
    Raises:
        ValueError: When something goes wrong.
    
    Example:
        ```python
        result = my_function("hello", 42)
        print(result)  # True
        ```
    """
    pass
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=echo_kernel

# Run specific test file
python -m pytest tests/test_echo_kernel.py
```

### Writing Tests
- Write tests for all new functionality
- Use descriptive test names
- Test both success and error cases
- Mock external dependencies (APIs, databases)

### Example Test
```python
import pytest
from echo_kernel import EchoKernel

def test_echo_kernel_initialization():
    """Test that EchoKernel initializes correctly."""
    kernel = EchoKernel()
    assert kernel.providers == []
    assert kernel._tools == {}
```

## 🔧 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write your code following the style guidelines
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run the test suite
python -m pytest

# Run examples to ensure they still work
python examples/task-decomposer.py
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature description

- Detailed description of changes
- Any breaking changes
- Related issues"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Examples still work
- [ ] No sensitive data is included

### Pull Request Template
```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Examples tested

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive data included
```

## 🐛 Bug Reports

When reporting bugs, please include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, EchoKernel version
- **Code Example**: Minimal code example that reproduces the issue

## 💡 Feature Requests

When suggesting features:
- **Description**: Clear description of the feature
- **Use Case**: Why this feature would be useful
- **Implementation**: Any thoughts on how it could be implemented
- **Alternatives**: Any existing workarounds

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Ask for help in pull requests

## 🎉 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to EchoKernel! 🚀 