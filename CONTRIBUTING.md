# Contributing to Solakon ONE Home Assistant Integration

Thank you for your interest in contributing to this project! This document provides guidelines and best practices for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Version Management and Release Process](#version-management-and-release-process)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Issue Guidelines](#issue-guidelines)
- [Code Style](#code-style)

## Code of Conduct

This project follows the standard open source code of conduct. Be respectful, constructive, and helpful to all contributors.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. Check if the bug has already been reported in [Issues](https://github.com/solakon-de/solakon-one-homeassistant/issues)
2. Collect relevant information (Home Assistant version, integration version, logs)

When filing a bug report, include:
- Clear and descriptive title using the `bug` label
- Steps to reproduce the issue
- Expected vs. actual behavior
- Home Assistant version and integration version
- Relevant log entries from Home Assistant
- Your configuration (remove sensitive information)

### Suggesting Features

Feature suggestions are welcome! Please:
1. Check if the feature has already been suggested
2. Use the `feature` label
3. Provide a clear use case and description
4. Explain why this feature would be useful

### Improving Documentation

Documentation improvements are always appreciated:
- Fix typos or unclear explanations
- Add missing information
- Provide usage examples
- Update outdated content
- Use the `documentation` label for documentation PRs

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Home Assistant development environment
- Git
- Text editor or IDE (VS Code recommended)

### Setting Up Development Environment

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/solakon-one-homeassistant.git
cd solakon-one-homeassistant
```

2. Create a development branch:
```bash
git checkout -b feature/your-feature-name
```

3. Make your changes in the `custom_components/solakon_one` directory

4. Test your changes in a Home Assistant development instance

### Testing

Before submitting changes:
1. Test the integration with a real Solakon ONE device if possible
2. Verify all existing functionality still works
3. Run hassfest validation
4. Check for Python code style issues with ruff

## Version Management and Release Process

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version (X.0.0): Breaking changes
- **MINOR** version (0.X.0): New features, backwards compatible
- **PATCH** version (0.0.X): Bug fixes, backwards compatible

### For Maintainers: Creating a Release

#### 1. Update CHANGELOG.md

Before creating a release, update `CHANGELOG.md`:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature descriptions with issue numbers (#123)

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes with issue numbers (#456)

### Deprecated
- Features to be removed in future versions

### Removed
- Removed features

### Security
- Security-related changes
```

Move items from `[Unreleased]` to the new version section.

#### 2. Update manifest.json

Update the version in `custom_components/solakon_one/manifest.json`:

```json
{
  "version": "X.Y.Z"
}
```

#### 3. Commit and Push Changes

```bash
git add CHANGELOG.md custom_components/solakon_one/manifest.json
git commit -m "chore: prepare release vX.Y.Z"
git push origin main
```

#### 4. Create Release via GitHub Actions

1. Go to **Actions** tab in GitHub
2. Select **Release** workflow
3. Click **Run workflow**
4. Enter the version number (e.g., `1.0.0`)
5. Select if it's a pre-release
6. Click **Run workflow**

This will:
- Create a git tag `vX.Y.Z`
- Create a GitHub release with changelog
- Generate release notes from PRs

#### 5. Verify Release

1. Check the [Releases page](https://github.com/solakon-de/solakon-one-homeassistant/releases)
2. Verify the release notes are correct
3. Test installation from HACS

### Release Drafter

The repository uses Release Drafter to automatically create draft releases:
- Triggered on every push to `main`
- Groups changes by labels (bug, feature, documentation, etc.)
- Creates draft release notes
- Maintainers can review and publish

## Pull Request Guidelines

### Before Submitting

1. Create an issue describing the change (for significant changes)
2. Create a feature branch from `main`
3. Make your changes with clear, logical commits
4. Update documentation if needed
5. Update CHANGELOG.md in the `[Unreleased]` section
6. Test your changes

### PR Title and Description

- Use clear, descriptive titles
- Reference related issues (e.g., "Fixes #123")
- Describe what changed and why
- Include testing steps if applicable
- Use appropriate labels:
  - `bug` for bug fixes
  - `feature` or `new-feature` for new features
  - `enhancement` for improvements
  - `documentation` for docs
  - `breaking-change` if it breaks compatibility

### PR Labels Guide

Apply the appropriate labels to help with automatic changelog generation:

**Type Labels:**
- `bug` / `bugfix`: Bug fixes
- `feature` / `new-feature`: New features
- `enhancement`: Improvements to existing features
- `documentation`: Documentation updates
- `maintenance`: Code maintenance and refactoring
- `ci`: CI/CD changes

**Priority Labels:**
- `priority:high`: Critical issues
- `priority:medium`: Important but not critical
- `priority:low`: Nice to have

**Version Impact:**
- `breaking-change`: Breaking changes (major version)
- `major`: Major version bump required
- `minor`: Minor version bump (new features)
- The absence of these labels implies a patch version

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Changes are covered by existing tests or new tests added
- [ ] Documentation updated (README.md, ENTITY_DOCUMENTATION.md if applicable)
- [ ] CHANGELOG.md updated in `[Unreleased]` section
- [ ] All workflows pass (hassfest, ruff)
- [ ] Tested with Home Assistant
- [ ] No security vulnerabilities introduced

## Issue Guidelines

### Using Labels

When creating or triaging issues, use these labels:

**Type Labels:**
- `bug`: Something isn't working
- `feature`: New feature request
- `enhancement`: Improvement to existing feature
- `documentation`: Documentation issue
- `question`: Question about usage

**Status Labels:**
- `good first issue`: Good for new contributors
- `help wanted`: Extra attention needed
- `wontfix`: Won't be fixed/implemented
- `duplicate`: Already reported

### Issue Templates

When creating issues, provide:
- **Bug reports**: Steps to reproduce, expected vs actual behavior, versions, logs
- **Feature requests**: Use case, proposed solution, alternatives considered
- **Questions**: What you're trying to achieve, what you've tried

## Code Style

### Python Code

- Follow PEP 8 style guide
- Use type hints where possible
- Use meaningful variable and function names
- Keep functions focused and small
- Add docstrings for public functions and classes
- Run `ruff` linter before committing

### Example Code Structure

```python
"""Module for handling Solakon ONE sensors."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant


class SolakonSensor(SensorEntity):
    """Representation of a Solakon ONE sensor."""

    def __init__(self, name: str, unit: str | None = None) -> None:
        """Initialize the sensor."""
        self._name = name
        self._unit = unit
        self._state: Any = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name
```

### Documentation Style

- Use Markdown for documentation files
- Keep line length reasonable (80-120 characters)
- Use clear headings and structure
- Include code examples where helpful
- Link to related documentation

## Getting Help

If you need help:
- Check existing [documentation](README.md) and [entity guide](ENTITY_DOCUMENTATION.md)
- Search [existing issues](https://github.com/solakon-de/solakon-one-homeassistant/issues)
- Ask questions in a new issue with the `question` label
- Be patient and respectful

## Recognition

Contributors will be recognized in:
- GitHub's contributor list
- Release notes (via Release Drafter)
- Special mentions for significant contributions

Thank you for contributing! 🎉
