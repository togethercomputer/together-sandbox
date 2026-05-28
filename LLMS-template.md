<!--
  This file is the source template for the per-package LLMS.md.
  It is rendered by bundle-docs.sh into:
    - together-sandbox-typescript/LLMS.md
    - together-sandbox-python/LLMS.md
  with the following tokens substituted per package:
    {{LANGUAGE}}         e.g. "TypeScript" or "Python"
    {{INSTALL_COMMAND}}  e.g. "npm install together-sandbox" or "pip install together-sandbox"
  Edit this file (not the generated LLMS.md) to change the bundled guide.
-->

# together-sandbox ({{LANGUAGE}})

Agent/LLM guide for the **together-sandbox** {{LANGUAGE}} SDK. The full API
reference and CLI reference are bundled alongside this file — see below.

## Installation

```bash
{{INSTALL_COMMAND}}
```

## Authentication

Set your Together AI API key as an environment variable before using the SDK or CLI:

```bash
export TOGETHER_API_KEY=your_api_key
```

## Bundled documentation

| Doc                                          | What's inside                                                                                                |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [SDK reference](./docs/sdk.md)               | Complete API surface for this {{LANGUAGE}} SDK — clients, namespaces, methods, error handling, retry config. |
| [CLI reference](./docs/cli.md)               | The `together-sandbox` CLI for building and publishing snapshots.                                            |
| [Sandboxes & snapshots](./docs/sandboxes.md) | Conceptual overview — what a sandbox is, what a snapshot is, how they relate.                                |

## Environment variables

| Variable            | Description                                     |
| ------------------- | ----------------------------------------------- |
| `TOGETHER_API_KEY`  | Required. Your Together AI API key.             |
| `TOGETHER_BASE_URL` | Optional. Override the management API base URL. |

## Source & issues

- Repository: https://github.com/togethercomputer/together-sandbox
- File issues or feature requests on GitHub.
