# Together Sandbox

Tools for working with Together AI sandboxes: a CLI, a TypeScript SDK, and a Python SDK.

## CLI

### Installation

```bash
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash
```

This installs `together-sandbox` to `/usr/local/bin`. To install a specific version or to a different directory:

```bash
VERSION=v1.2.3 bash <(curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh)
INSTALL_DIR=$HOME/.local/bin bash <(curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh)
```

### Authentication

Set your Together AI API key:

```bash
export TOGETHER_API_KEY=your_api_key
```

### Commands

#### `sandboxes`

```
together-sandbox sandboxes list [options]
  -o, --output     Comma-separated fields: id,title,privacy,tags,createdAt,updatedAt
  -t, --tags       Filter by tags (comma-separated)
  -s, --status     Filter by status (running)
  -p, --page       Page number
      --page-size  Items per page
      --since      Filter by creation date
      --order-by   Order by field (inserted_at, updated_at)
      --direction  Sort direction (asc, desc)
  -l, --limit      Maximum number of sandboxes to list (default: 100)

together-sandbox sandboxes fork <id>

together-sandbox sandboxes hibernate [id]    # reads from stdin if no ID given

together-sandbox sandboxes shutdown [id]     # reads from stdin if no ID given
```

#### `host-tokens`

```
together-sandbox host-tokens list <sandbox-id>

together-sandbox host-tokens create <sandbox-id> --expires-at <date>
  -e, --expires-at  Expiration date in ISO 8601 format (e.g. 2024-12-31T23:59:59Z)

together-sandbox host-tokens update <sandbox-id> <host-token-id> [--expires-at <date>]

together-sandbox host-tokens revoke <sandbox-id> [host-token-id]
  -a, --all  Revoke all tokens for the sandbox
```

#### `preview-hosts`

```
together-sandbox preview-hosts list

together-sandbox preview-hosts add <host>

together-sandbox preview-hosts remove <host>

together-sandbox preview-hosts clear
```

#### `build`

Builds and deploys a sandbox from the current directory.

```bash
together-sandbox build
```

---

## TypeScript SDK

> **Note:** The package is not yet published. The instructions below show how to install it once it is available on npm.

```bash
npm install @together-sandbox/sdk
```

### Usage

```typescript
import { API } from "@together-sandbox/sdk";

const api = new API({ apiKey: process.env.TOGETHER_API_KEY });

// List sandboxes
const { sandboxes } = await api.listSandboxes();

// Fork a sandbox
const forked = await api.forkSandbox("sandbox-id");

// Hibernate or shut down a sandbox
await api.hibernate("sandbox-id");
await api.shutdown("sandbox-id");

// Preview tokens
const { tokens } = await api.listPreviewTokens("sandbox-id");
const { token } = await api.createPreviewToken("sandbox-id", {
  expires_at: "2024-12-31T23:59:59Z",
});
await api.revokeAllPreviewTokens("sandbox-id");

// Preview hosts
const { preview_hosts } = await api.listPreviewHosts();
await api.updatePreviewHost({ hosts: ["example.com"] });
```

### Generated clients

Both OpenAPI clients are also exported as namespaces for lower-level access:

```typescript
import { api, sandbox } from "@together-sandbox/sdk";

// Use raw generated functions from the API client
const result = await api.sandboxList({ client: myClient });

// Use raw generated functions from the Sandbox client
const exec = await sandbox.createExec({ client: myClient });
```

---

## Python SDK

> **Note:** The package is not yet published. The instructions below show how to install it once it is available on PyPI.

```bash
pip install together-sandbox
```

### Usage

```python
from together_sandbox import ApiClient, SandboxClient

api_client = ApiClient(base_url="https://api.together.ai/csb/sdk", token="your_api_key")
sandbox_client = SandboxClient(base_url="...", token="your_token")
```

`ApiClient` and `SandboxClient` are fully generated from the OpenAPI specs. Refer to the generated module docstrings for available methods.

### Regenerating clients

If the OpenAPI specs change, regenerate the Python clients:

```bash
cd together-sandbox-python
pip install openapi-python-client
bash generate.sh
```
