# Experimental features

The features on this page are **experimental**. They may change or be removed at short notice, and are not covered by the rest of the documentation.

They are set with the `experimental` parameter when creating a sandbox. The SDKs and the CLI take it exactly as the API does — the same field names, the same shape — and send it as is:

| Client     | Parameter                                                   |
| ---------- | ----------------------------------------------------------- |
| API        | `experimental` in the `POST /sandboxes` body                |
| TypeScript | `experimental` in `sdk.sandboxes.create(...)` (type `CreateSandboxExperimental`) |
| Python     | `experimental=` dict in `sdk.sandboxes.create(...)`          |
| CLI        | `--experimental '<json>'` on `sandboxes create` and `sandboxes run` |

A sandbox returns what it was created with in its own `experimental` field.

---

## Network policy

`experimental.network_policy` sets who can reach the sandbox's ports through its URL (`https://<sandbox-id>-<port>.…`). Only **inbound** traffic is covered for now; outbound rules will come later.

- **Without a network policy**, every port is open to everyone.
- **With a network policy**, every inbound request is blocked, except those its `inbound_allowlist` admits.

```json
{
  "network_policy": {
    "inbound_allowlist": [
      { "ports": ["80", "8000-8100"] },
      { "ports": ["3000"], "requires_token": true },
      { "ports": ["*"], "from": ["10.0.0.0/8"] }
    ]
  }
}
```

This opens port 80 and ports 8000–8100 to everyone, port 3000 to anyone holding the agent token, and every port to the `10.0.0.0/8` network (port 3000 still needs the token there too, see below). Everything else is closed.

### Rules

Each rule of `inbound_allowlist` (at most 128) admits requests:

| Field            | Description                                                                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `ports`          | Required. The ports: single ports (`"80"`), inclusive ranges (`"8000-8100"`), or `"*"` for every port. Strings; at most 64 entries.         |
| `from`           | Optional. The clients: `"*"`, IPs, or CIDRs. Defaults to `["*"]`, every client. At most 64 entries.                                          |
| `requires_token` | Optional, default `false`. When `true`, a request is admitted only if it carries the sandbox's agent token (`agent.token`) in the `X-Sandbox-Token` header. |

### How a request is decided

A request is admitted when a rule covers its port and its client. Otherwise it is refused with `403`.

Rules can overlap. When several rules cover a request, **`requires_token` wins**: if any of them requires the token, the request must carry it, even if another rule covering it needs none. So you can open a port to everyone and still require the token from some clients:

```json
{ "inbound_allowlist": [
  { "ports": ["80"] },
  { "ports": ["80"], "from": ["1.2.3.4"], "requires_token": true }
] }
```

Here `1.2.3.4` needs the token on port 80; every other client does not. Likewise, `{ "ports": ["*"], "requires_token": true }` puts the token on every port, whatever other rules open.

Also:

- An empty allowlist (`"inbound_allowlist": []`) closes every port.
- `X-Sandbox-Token` is always removed before the request reaches the sandbox.
- The agent port (57468, used by the SDKs) is never filtered: the agent authenticates every request itself.
- An invalid policy (an empty `ports` list, a bad port, range, IP or CIDR) is rejected when the sandbox is created.

### Response

A sandbox returns its policy in `experimental.network_policy`, or `null` without one, with the defaults filled in:

```json
"experimental": {
  "network_policy": {
    "inbound_allowlist": [
      { "ports": ["80", "8000-8100"], "from": ["*"], "requires_token": false },
      { "ports": ["3000"], "from": ["*"], "requires_token": true }
    ]
  }
}
```

### Examples

TypeScript:

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
  experimental: {
    network_policy: {
      inbound_allowlist: [
        { ports: ["80"], from: ["10.0.0.0/8"] },
        { ports: ["3000"], requires_token: true },
      ],
    },
  },
});

// Reach a token-protected port.
await fetch(`https://${sandbox.id}-3000.<domain>/`, {
  headers: { "X-Sandbox-Token": sandbox.vmInfo.agent.token! },
});
```

Python:

```python
sandbox = await sdk.sandboxes.create(
    snapshot_alias="my-app@v1",
    experimental={
        "network_policy": {
            "inbound_allowlist": [
                {"ports": ["80"], "from": ["10.0.0.0/8"]},
                {"ports": ["3000"], "requires_token": True},
            ]
        }
    },
)
```

CLI (`sandboxes get` shows the rules under **Experimental**):

```bash
together-sandbox sandboxes create @my-app@v1 --experimental '{
  "network_policy": {"inbound_allowlist": [
    {"ports": ["80"], "from": ["10.0.0.0/8"]},
    {"ports": ["3000"], "requires_token": true}
  ]}
}'
```
