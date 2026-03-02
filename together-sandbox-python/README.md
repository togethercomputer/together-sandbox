# together-sandbox

Python SDK for the Together Sandbox API.

## Installation

```bash
pip install together-sandbox
```

Requires Python 3.12+.

## Usage

The SDK exposes two async clients:

- **`ApiClient`** — manages sandboxes (create, fork, start, shutdown, etc.)
- **`SandboxClient`** — interacts with a running sandbox via its Pint URL (filesystem, execs, SSE streams, etc.)

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
