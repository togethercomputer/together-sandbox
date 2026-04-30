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

## Tests

Read [tests/README.md](./tests/README.md)
