# Release Process

This document describes the release process for Together Sandbox, managed by Release Please.

## Overview

Releases are automated using [Release Please](https://github.com/googleapis/release-please), which:

1. Monitors commits to `main` branch
2. Creates Release PRs with version bumps and changelogs
3. Creates GitHub Releases when Release PRs are merged
4. Triggers artifact builds and package publishing

## How to Trigger a Release

### Automatic (Recommended)

1. Make commits using conventional commit format:
   ```bash
   feat: add new sandbox creation API
   fix: correct token expiration handling
   ```

2. Merge your PR to `main`

3. Release Please will automatically create or update a Release PR

4. Review and merge the Release PR

5. GitHub Release is created automatically

### Manual Trigger

You can manually trigger the release workflow:

1. Go to **Actions** → **Release Please** in GitHub
2. Click **Run workflow**
3. Select the branch (usually `main`)
4. Click **Run workflow**

## Release PR Workflow

When commits are merged to `main`:

```
Commits merged to main
        │
        ▼
Release Please analyzes commits
        │
        ▼
Creates/updates Release PR
        │
        ▼
Maintainer reviews PR
        │
        ▼
Merge Release PR
        │
        ▼
GitHub Release created
        │
        ▼
Build artifacts workflow runs
        │
        ▼
Artifacts uploaded to release
        │
        ▼
TypeScript SDK published to GitHub Packages
```

## What Happens After Release

### GitHub Release

A GitHub Release is created with:
- Release notes from changelog
- Tag name: `together-sandbox-typescript-v1.0.0`, `together-sandbox-python-v1.0.0`, `together-sandbox-cli-v1.0.0`

### Artifacts Built and Uploaded

| Artifact | Description |
|----------|-------------|
| `together-sandbox-sdk.tgz` | TypeScript SDK tarball |
| `together-sandbox-darwin-arm64` | CLI for macOS ARM |
| `together-sandbox-darwin-x64` | CLI for macOS Intel |
| `together-sandbox-linux-x64` | CLI for Linux x64 |
| `together-sandbox-linux-arm64` | CLI for Linux ARM |
| `together-sandbox-windows-x64.exe` | CLI for Windows |

### Package Publishing

| Package | Destination |
|---------|-------------|
| `@togethercomputer/together-sandbox-sdk` | GitHub Packages |
| `together-sandbox` (Python) | No publishing (git install only) |

## Installation After Release

### TypeScript SDK (GitHub Packages)

Users install with:

```bash
# Configure npm to use GitHub Packages for this scope
echo "@togethercomputer:registry=https://npm.pkg.github.com" >> .npmrc

# Install the package
npm install @togethercomputer/together-sandbox-sdk
```

### Python SDK (Git Subdirectory)

Users install with:

```bash
# Latest version
pip install git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python

# Specific version
pip install git+https://github.com/togethercomputer/together-sandbox.git@together-sandbox-python-v1.0.0#subdirectory=together-sandbox-python
```

### CLI Binary

Users download from GitHub Releases:

```bash
# Using install script
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash

# Or download directly
curl -LO https://github.com/togethercomputer/together-sandbox/releases/latest/download/together-sandbox-linux-x64
chmod +x together-sandbox-linux-x64
```

## Version Bumping Rules

| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `feat:` | Minor (1.0.0 → 1.1.0) | New features |
| `fix:` | Patch (1.0.0 → 1.0.1) | Bug fixes |
| `feat!:` or `BREAKING CHANGE:` | Major (1.0.0 → 2.0.0) | Breaking changes |
| `docs:`, `chore:`, etc. | No bump | Non-functional changes |

## Troubleshooting

### Release PR Not Created

1. Ensure commits follow conventional commit format
2. Check that commits include `feat:` or `fix:` types
3. Verify the `release-please-config.json` is valid

### Build Artifacts Failed

1. Check the Actions tab for error logs
2. Verify `src/main.ts` exists (not `.tsx`)
3. Ensure all dependencies are properly declared

### TypeScript SDK Publishing Failed

1. Verify the package name is scoped: `@togethercomputer/together-sandbox-sdk`
2. Check GitHub Packages permissions in workflow
3. Ensure `publishConfig.registry` is set correctly

### Python Version Not Updated

1. Verify `pyproject.toml` has `[project]` table with `version` field
2. Check that release-type is set to `python` in config

## Manual Release (Emergency)

If the automated workflow fails, you can manually create a release:

```bash
# 1. Create and push a tag
git tag together-sandbox-typescript-v1.0.0
git push origin together-sandbox-typescript-v1.0.0

# 2. Build artifacts locally
npm ci
npm run build --workspace=together-sandbox-typescript
npm pack --workspace=together-sandbox-typescript

# 3. Upload to GitHub Releases manually
# Go to Releases → Draft a new release → Upload artifacts
```

## Configuration Files

| File | Purpose |
|------|---------|
| `release-please-config.json` | Release Please configuration |
| `.release-please-manifest.json` | Current version tracking |
| `.github/workflows/release-please.yml` | Release automation workflow |
| `.github/workflows/lint.yml` | Commitlint validation |
