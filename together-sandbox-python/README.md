# together-sandbox

Python SDK for the Together Sandbox API.

## Installation

### From GitHub (Recommended)

Since the package is not published to PyPI, install it directly from the GitHub repository:

```bash
# Latest from main branch
pip install "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"

# Specific version (tag)
pip install "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git@v1.0.0#subdirectory=together-sandbox-python"

# Specific commit
pip install "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git@abc123#subdirectory=together-sandbox-python"
```

### With Authentication (Private Repositories)

For private repositories, use SSH or a Personal Access Token:

```bash
# Using SSH (recommended for developers)
pip install "git+ssh://git@github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"

# Using a GitHub PAT
pip install "git+https://YOUR_TOKEN@github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"
```

### In requirements.txt

```text
together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python
```

### In pyproject.toml

```toml
[project]
dependencies = [
    "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python",
]
```

### From PyPI (When Available)

```bash
pip install together-sandbox
```

Requires Python 3.12+.

## Quick Start

```python
import asyncio
from together_sandbox import TogetherSandbox

async def main():
    # api_key defaults to TOGETHER_API_KEY environment variable
    sdk = TogetherSandbox(api_key="your-api-key")

    # Start a sandbox — URL/token wiring is handled automatically
    async with await sdk.sandboxes.start("your-sandbox-id") as sb:
        # Read a file
        content = await sb.files.read_file("/package.json")
        print(content)

        # Run a command
        from together_sandbox.sandbox.models.create_exec_request import CreateExecRequest
        exec_item = await sb.execs.create_exec(
            CreateExecRequest(command="echo", args=["Hello, sandbox!"])
        )

asyncio.run(main())
```

### E2B-style: classmethod factory

```python
from together_sandbox import Sandbox

sandbox = await Sandbox.start("your-sandbox-id", api_key="your-key")
```

## Low-level Usage (Advanced)

The generated clients are still fully exported for direct use:

```python
import asyncio
import os

from together_sandbox.api import APIClient as ApiClient
from together_sandbox.api import ClientConfig, HttpxTransport
from together_sandbox.sandbox import APIClient as SandboxClient
from together_sandbox.sandbox import ClientConfig as SandboxConfig
from together_sandbox.sandbox import HttpxTransport as SandboxTransport
from together_sandbox.sandbox.models.create_exec_request import CreateExecRequest


async def main():
    api_key = os.environ["TOGETHER_API_KEY"]
    base_url = os.environ.get("TOGETHER_BASE_URL", "https://api.codesandbox.io")

    async with ApiClient(
        ClientConfig(base_url=base_url),
        transport=HttpxTransport(base_url, bearer_token=api_key),
    ) as client:
        # Fork a sandbox from a template
        fork_result = await client.sandbox.sandbox_fork("your-template-id")
        sandbox_id = fork_result.data_.id_

        # Start the sandbox
        start_result = await client.vm.vm_start(sandbox_id)
        pint_url = start_result.data_.pint_url
        pint_token = start_result.data_.pint_token

        # Connect to the running sandbox via Pint
        async with SandboxClient(
            SandboxConfig(base_url=pint_url),
            transport=SandboxTransport(pint_url, bearer_token=pint_token),
        ) as sb:
            # Create an exec
            exec_item = await sb.execs.create_exec(
                CreateExecRequest(command="echo", args=["Hello, sandbox!"])
            )
            print(f"Created exec {exec_item.id_}")

            # Stream exec status updates via SSE.
            # stream_execs_list() is an async generator — each event is a dict.
            async for event in sb.execs.stream_execs_list():
                execs = event.get("execs", [])
                our = next((e for e in execs if e.get("id") == exec_item.id_), None)
                if our:
                    print(f"  [{our['status']}] pid={our['pid']}")
                    if our["status"] in ("finished", "stopped"):
                        break

        # Shut down when done
        await client.vm.vm_shutdown(sandbox_id)


asyncio.run(main())
```

## Clients and namespaces

### `ApiClient` — management API

| Namespace | Methods |
|---|---|
| `client.sandbox` | `sandbox_list`, `sandbox_create`, `sandbox_get`, `sandbox_fork` |
| `client.vm` | `vm_start`, `vm_shutdown`, `vm_hibernate`, `vm_delete`, … |
| `client.meta` | `meta_information` |

### `SandboxClient` — in-sandbox (Pint) API

| Namespace | Methods |
|---|---|
| `sb.execs` | `create_exec`, `list_execs`, `get_exec`, `get_exec_output`, `stream_execs_list` |
| `sb.files` | `read_file`, `create_file`, `delete_file`, `perform_file_action` |
| `sb.directories` | `list_directory`, `create_directory`, `delete_directory` |
| `sb.ports` | `list_ports`, `stream_ports_list` |
| `sb.streams` | `create_watcher` |
| `sb.tasks` | `list_tasks`, `get_task`, `execute_task_action` |

## SSE streams

`stream_execs_list`, `stream_ports_list`, and `create_watcher` are async generators.
Iterate them directly with `async for` — no `await` needed on the call itself:

```python
async for event in sb.execs.stream_execs_list():
    print(event)  # dict[str, Any], JSON-parsed from the SSE event data
```

## Environment variables

| Variable | Description |
|---|---|
| `TOGETHER_API_KEY` | Your Together / CodeSandbox API key |
| `TOGETHER_BASE_URL` | Override the API base URL (default: `https://api.codesandbox.io`) |
