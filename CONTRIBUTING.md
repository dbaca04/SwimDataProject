# Contributing to Swim Data Project

We're thrilled that you're interested in contributing to the Swim Data Project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and positive community.

## How to Contribute

### Reporting Bugs

If you find a bug in the project:

1. Check if the bug has already been reported in the [Issues](https://github.com/dbaca04/SwimDataProject/issues) section.
2. If not, create a new issue using the bug report template.
3. Include as much detail as possible: steps to reproduce, expected behavior, screenshots, and environment details.

### Suggesting Features

Have an idea for a new feature or improvement?

1. Check if the feature has already been suggested in the [Issues](https://github.com/dbaca04/SwimDataProject/issues) section.
2. If not, create a new issue using the feature request template.
3. Clearly describe the problem and your proposed solution.

### Pull Requests

We welcome pull requests for bug fixes, features, and improvements:

1. Fork the repository and create a new branch from `master`.
2. Make your changes, following the coding standards and practices.
3. Add or update tests as needed.
4. Update documentation if necessary.
5. Create a pull request with a clear description of the changes.

## Development Setup

See the [Getting Started](./SwimDataProject/getting-started.md) guide for instructions on setting up your development environment.

## Coding Standards

- Follow PEP 8 style guide for Python code.
- Write clear, descriptive commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) format.
- Include appropriate comments and docstrings.
- Write tests for new functionality.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Where `<type>` is one of:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: Code changes that neither fix a bug nor add a feature
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Changes to the build process or auxiliary tools

### Branch Naming Convention

- **feature/**: For new features
- **bugfix/**: For bug fixes
- **docs/**: For documentation updates
- **refactor/**: For code refactoring
- **test/**: For adding or updating tests

Example: `feature/add-swimcloud-scraper`

## Testing

- Write tests for new functionality.
- Ensure all tests pass before submitting a pull request.
- Run tests using pytest:
  ```
  pytest
  ```

## Documentation

- Update documentation for new features or changes to existing functionality.
- Use clear, concise language in documentation.
- Include examples when appropriate.

## Review Process

All submissions will be reviewed by the project maintainers:

1. Code will be reviewed for quality, style, and adherence to the project's standards.
2. Tests will be verified to ensure they pass and provide adequate coverage.
3. Documentation will be checked for clarity and completeness.

## Thank You!

Thank you for contributing to the Swim Data Project. Your efforts help make this project better for everyone!
