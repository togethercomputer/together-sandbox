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

### Classmethod factory

```python
from together_sandbox import Sandbox

sandbox = await Sandbox.start("your-sandbox-id", api_key="your-key")
```

## Snapshots

```python
from together_sandbox import TogetherSandbox, CreateFromContextParams, CreateFromImageParams

sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env

# Build from a local Dockerfile
result = await sdk.snapshots.create(
    CreateFromContextParams(
        context="./my-app",
        dockerfile="./Dockerfile",  # optional
        alias="my-app@latest",      # optional
    )
)

# Register a public Docker image
result = await sdk.snapshots.create(
    CreateFromImageParams(
        image="node:20-alpine",
        alias="node@20",  # optional
    )
)

print(result.snapshot_id)  # pass to sdk.sandboxes.start()
print(result.alias)        # "my-app@latest"
```

## Environment variables

| Variable            | Description                                                       |
| ------------------- | ----------------------------------------------------------------- |
| `TOGETHER_API_KEY`  | Your Together / CodeSandbox API key                               |
| `TOGETHER_BASE_URL` | Override the API base URL (default: `https://api.codesandbox.io`) |
