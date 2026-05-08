# together-sandbox (Python)

Developer guide for the `together-sandbox` Python SDK.

[SDK Docs](../docs/python-sdk.md)

> **Note:** The generated OpenAPI clients (`together_sandbox/api/` and
> `together_sandbox/sandbox/`) are committed to the repository temporarily until
> the package is published to PyPI. Once published they will be removed from
> version control and regenerated as part of the install/build step instead.

## Generating the OpenAPI clients

The SDK wraps two auto-generated OpenAPI clients. Regenerate them whenever an
OpenAPI spec changes (both specs live in the repo root):

```bash
# From the repo root
bash generate.sh
```

This runs `together-sandbox-python/generate.sh` which invokes
`openapi-python-client` against `api-openapi.json` and `sandbox-openapi.json`
and writes the output to:

- `together_sandbox/api/` — management API client
- `together_sandbox/sandbox/` — in-VM sandbox API client

**Never edit those directories by hand** — they are overwritten on every run.

## Tests

## Prerequisites

1. Together AI API key
2. Python 3.10 or higher
3. Install dev dependencies:

```bash
cd together-sandbox-python
pip install .[dev]
```

4. Set up a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

5. Create a snapshot to run the tests with

```bash
node ./together-sandbox-cli/dist/together-sandbox.mjs snapshots create --context ./test-template
```

## Environment Variables

Set the following environment variables before running e2e tests:

```bash
# Required
export TOGETHER_API_KEY="your-api-key-here"

# Optional
export TOGETHER_SNAPSHOT_ID="snapshot-id"  # If you want to test with a specific snapshot
export TOGETHER_BASE_URL="https://api.codesandbox.io"  # Override default base URL
```

## Running Tests

**Note:** All `pytest` commands must be run from the `together-sandbox-python/` directory.

### Unit tests

```bash
pytest tests/ -v
```

### Run all e2e tests

```bash
pytest tests/e2e/ -v
```

### Run specific e2e test file

```bash
pytest tests/e2e/test_sandbox_filesystem.py -v
```

### Run specific test class or function

```bash
# Run a specific test class
pytest tests/e2e/test_sandbox_filesystem.py::TestSandboxFilesystem -v

# Run a specific test function
pytest tests/e2e/test_sandbox_filesystem.py::TestSandboxFilesystem::test_write_and_read_text_file -v
```

### Run with output from print statements

```bash
pytest tests/e2e/ -v -s
```

## Test Structure

### Fixtures (e2e/helpers.py)

The `helpers.py` module provides pytest fixtures that handle sandbox lifecycle:

- `sdk`: Provides a configured `TogetherSandbox` instance
- `sandbox`: Creates a sandbox instance and automatically cleans it up after tests
- `retry_until`: Helper function for polling operations

Example usage in tests:

```python
@pytest.mark.asyncio
async def test_something(sandbox: Sandbox):
    # sandbox is automatically created and will be cleaned up
    await sandbox.files.create_file("/test.txt", "content")
    result = await sandbox.files.read_file("/test.txt")
    assert result.content == "content"
```

## Test Patterns

### Using the sandbox fixture

Most tests should use the `sandbox` fixture which handles creation and cleanup:

```python
async def test_my_feature(sandbox: Sandbox):
    # Your test code here
    # Sandbox will be automatically cleaned up
    pass
```

### Manual sandbox management

For lifecycle tests that need explicit control:

```python
async def test_lifecycle():
    sdk = TogetherSandbox(api_key=get_api_key())
    try:
        sandbox = await sdk.sandboxes.start(template_id)
        # Test code
    finally:
        await sdk.sandboxes.shutdown(sandbox.id)
        await sdk.close()
```

### Retry polling pattern

For operations that may take time:

```python
from .helpers import retry_until

result = await retry_until(
    lambda: sandbox.files.read_file("/path"),
    lambda r: r.content == "expected",
    timeout=5.0,
    interval=0.1
)
```

## Notes

- E2E tests connect to real sandbox instances and may incur API costs
- Tests automatically clean up sandboxes, but interrupted tests may leave orphaned sandboxes
- Some exec tests are placeholders and may need implementation based on the actual API structure
- Binary file tests verify the application/octet-stream content type handling
- Timeout for sandbox cleanup is set to 10 seconds to prevent hanging

## Troubleshooting

### Tests skip with "TOGETHER_API_KEY environment variable not set"

Make sure you've exported the `TOGETHER_API_KEY` environment variable:

```bash
export TOGETHER_API_KEY="your-api-key"
```

### Tests fail with timeout errors

The sandbox may be taking longer to start or respond. You can:

1. Check your network connection
2. Verify the API service status
3. Increase timeout values in the tests if needed

### Tests fail with authentication errors

Verify your API key is valid and has the necessary permissions for:

- Creating sandboxes
- Reading/writing files
- Managing sandbox lifecycle

### Orphaned sandboxes

If tests are interrupted, sandboxes may not be cleaned up. You can manually delete them using the API or wait for automatic cleanup policies.
