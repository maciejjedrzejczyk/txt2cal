# Contributing to txt2cal

Thank you for your interest in contributing to txt2cal! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/yourusername/txt2cal/issues)
- Use the bug report template when creating a new issue
- Include detailed steps to reproduce the bug
- Include screenshots if applicable
- Specify your environment (browser, OS, etc.)

### Suggesting Enhancements

- Check if the enhancement has already been suggested in the [Issues](https://github.com/yourusername/txt2cal/issues)
- Use the feature request template when creating a new issue
- Clearly describe the problem and solution
- Explain why this enhancement would be useful

### Pull Requests

- Fill in the required template
- Follow the [coding standards](#coding-standards)
- Include tests for new features or bug fixes
- Update documentation as needed

## Development Setup

See the [Development Guide](docs/development-guide.md) for detailed setup instructions.

### Quick Start

1. Fork and clone the repository
2. Install dependencies: `npm install` and `cd server && npm install`
3. Set up environment variables: `cp server/.env.example server/.env`
4. Start development servers: `npm run dev`

## Pull Request Process

1. Update the README.md and documentation with details of changes if applicable
2. Update the tests as appropriate
3. The PR should work for all supported browsers and environments
4. Ensure all tests pass: `npm test`
5. Get at least one code review from a maintainer

### PR Checklist

- [ ] Code follows the style guidelines
- [ ] Tests for the changes have been added
- [ ] Documentation has been updated
- [ ] Changes generate no new warnings
- [ ] Any dependent changes have been merged and published

## Coding Standards

### JavaScript

- Use ES6+ features
- Follow the existing code style
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

### React Components

- Use functional components with hooks
- Keep components small and focused on a single responsibility
- Use prop types for component props
- Follow the container/presentational component pattern when appropriate

### CSS

- Follow the existing CSS naming conventions
- Use responsive design principles
- Test on multiple screen sizes

## Testing Guidelines

- Write tests for all new features and bug fixes
- Maintain or improve test coverage
- Test edge cases and error conditions
- Follow the existing test patterns

### Running Tests

```bash
# Run all tests
npm test

# Run specific tests
npm test -- -t "calendar utils"

# Generate coverage report
npm test -- --coverage
```

## Documentation

- Update documentation for any changes to functionality
- Document new features, components, or APIs
- Keep the README.md up to date
- Use clear, concise language

## Community

### Communication Channels

- GitHub Issues: For bug reports, feature requests, and discussions
- Pull Requests: For code contributions

### Recognition

All contributors will be recognized in the [CONTRIBUTORS.md](CONTRIBUTORS.md) file.

## License

By contributing to txt2cal, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
