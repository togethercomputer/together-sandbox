# together-sandbox (Python)

Developer guide for the `together-sandbox` Python SDK.

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

## Running the tests

```bash
python -m venv .venv
source .venv/bin/activate
```

### Unit tests

```bash
pip install ".[dev]"
pytest tests/ -v
```

E2E tests are excluded by default (see below).

### End-to-end tests

E2E tests hit the real API and require Docker to be running locally (snapshot
builds use a Docker context under the hood). They are skipped automatically
unless `CSB_API_KEY` is set and the `-m e2e` flag is passed.

```bash
CSB_API_KEY=your-api-key pytest tests/ -v -m e2e
```

> E2E tests have a 300 s timeout per test. Make sure Docker is running before
> starting them.

Tests use `pytest` with `asyncio_mode = "auto"` (configured in `pyproject.toml`)
and `unittest.mock.AsyncMock` for mocking API calls in unit tests. See
`CLAUDE.md` for fuller testing conventions.
