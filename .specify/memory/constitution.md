# Project Constitution

## Core Principles

### I. Single File Python Programs
All Python programs must be self-contained in a single file for simplicity and portability. This ensures programs are easy to distribute, understand, and maintain without complex project structures.

### II. Best Practice Adherence
Follow PEP 8 style guidelines, use comprehensive type hints, implement proper error handling, and apply Python idioms. Code must be readable, maintainable, and professionally structured.

### III. Comprehensive Documentation
Include detailed docstrings for all modules, classes, and functions. Provide inline comments for complex logic, and include usage examples. Documentation should enable others to understand and use the code effectively.

### IV. Pydantic Integration
Use Pydantic for data validation, settings management, and type safety. This ensures robust data handling, clear schemas, and automatic validation throughout the application.

### V. Self-Contained Design
Minimize external dependencies while maintaining functionality and readability. Prefer standard library solutions where possible, and justify any external dependencies with clear benefits.

## Development Standards

### Code Quality Requirements
- All functions and classes must have type hints
- Error handling must be explicit and informative
- Code must pass linting (flake8, black, mypy)
- Performance considerations for data processing and API calls

### Testing Standards
- Include example usage in docstrings
- Provide error case examples
- Validate Pydantic models with test data
- Test edge cases and error conditions

## Governance

All code must comply with these constitutional principles. Any deviation requires explicit justification and approval. The constitution supersedes other coding preferences and ensures consistency across all Python programs in this project.

**Version**: 1.0.0 | **Ratified**: 2025-09-19 | **Last Amended**: 2025-09-19