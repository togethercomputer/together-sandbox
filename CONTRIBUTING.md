# Contributing to Together Sandbox

Thank you for your interest in contributing to Together Sandbox! This document outlines the guidelines for contributing to this project.

## Conventional Commits

This project uses **Conventional Commits** specification for commit messages. This is essential for our automated release workflow powered by Release Please.

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat` | A new feature | **Minor** bump (1.0.0 → 1.1.0) |
| `fix` | A bug fix | **Patch** bump (1.0.0 → 1.0.1) |
| `feat!` or `BREAKING CHANGE` | Breaking change | **Major** bump (1.0.0 → 2.0.0) |
| `docs` | Documentation changes | No version bump |
| `chore` | Maintenance tasks | No version bump |
| `refactor` | Code refactoring | No version bump |
| `test` | Adding tests | No version bump |
| `style` | Code style changes | No version bump |
| `perf` | Performance improvements | Patch bump |
| `ci` | CI/CD changes | No version bump |

### Examples

```bash
# Feature (minor version bump)
feat: add new sandbox creation API

# Bug fix (patch version bump)
fix: correct token expiration handling

# Breaking change (major version bump)
feat!: redesign API interface

# Or with BREAKING CHANGE footer
feat: redesign API interface

BREAKING CHANGE: The createSandbox function now requires an options object

# Documentation (no version bump)
docs: update README with examples

# Scoped changes
feat(cli): add --json flag for sandbox list command
fix(typescript): handle undefined response in client

# Multiple changes in one commit
feat(python): add async context manager support

This adds support for using the client as an async context manager
for automatic resource cleanup.

Closes #123
```

## Release Workflow

### How Releases Work

1. **Make commits** using conventional commit format
2. **Merge to main** - Release Please detects your commits
3. **Release PR created** - A PR is automatically created with version bumps and changelog updates
4. **Review and merge** - A maintainer reviews the Release PR
5. **Release created** - When the Release PR is merged, a GitHub Release is created
6. **Artifacts built** - SDK tarballs and CLI binaries are built and uploaded

### Release Flow Diagram

```
Commit (feat/fix) ──► Push to main ──► Release PR created ──► Review & Merge ──► GitHub Release ──► Artifacts Published
```

### Publishing Destinations

| Component | Destination |
|-----------|-------------|
| TypeScript SDK | GitHub Packages (`@togethercomputer/together-sandbox-sdk`) |
| Python SDK | Git subdirectory install (no publishing required) |
| CLI binaries | GitHub Release assets |

## Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following conventional commits
3. **Open a Pull Request** to merge into `main`
4. **Ensure CI passes** - linting, tests, and builds
5. **Request review** from maintainers
6. **Squash and merge** - your PR will be squash-merged

### PR Title Convention

PR titles should follow conventional commit format:

```
feat: add new feature
fix: resolve bug in X
docs: update documentation
refactor: improve Y
```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/togethercomputer/together-sandbox.git
cd together-sandbox

# Install dependencies
npm ci

# Build TypeScript SDK
npm run build --workspace=together-sandbox-typescript

# Build CLI
npm run build --workspace=together-sandbox-cli

# Regenerate API clients (if needed)
bash generate.sh
```

## Code Style

- **TypeScript**: Follow the existing code style, use TypeScript strict mode
- **Python**: Follow PEP 8, use type hints
- **Commit messages**: Follow conventional commits specification

## Questions?

Open an issue for questions, bug reports, or feature requests.
