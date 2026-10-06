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

`experimental.network_policy` sets who can reach the sandbox's ports through its URL (`https://<sandbox-id>-<port>.…`). Only **inbound** rules are supported for now; outbound rules will come later. Without a policy, every port is open to everyone.

```json
{
  "network_policy": {
    "inbound": [
      { "to_port": "80", "from": ["10.0.0.0/8", "203.0.113.7"], "access": "allow" },
      { "to_port": "3000-3999", "from": ["*"], "access": "allow_with_token" },
      { "to_port": "*", "from": ["*"], "access": "deny" }
    ]
  }
}
```

This allows port 80 from the office network only, admits ports 3000–3999 for anyone holding the agent token, and closes everything else (other ports, and port 80 from other clients).

### Rules

Each rule of `inbound` (at most 128) has:

| Field     | Description                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------ |
| `to_port` | A port, an inclusive range `"low-high"`, or `"*"` for every port. A string. Defaults to `"*"`.   |
| `from`    | The clients the rule applies to: `"*"`, IPs, or CIDRs. At least one, at most 64.                 |
| `access`  | `allow`, `deny`, or `allow_with_token`.                                                          |

| `access`           | Effect                                                                                                                                  |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `allow`            | The request goes through.                                                                                                               |
| `deny`             | The request is refused with `403`.                                                                                                      |
| `allow_with_token` | The request goes through only if it carries the sandbox's agent token (`agent.token`) in the `X-Sandbox-Token` header. Otherwise `403`. |

### Response

A sandbox returns its policy in `experimental.network_policy`, or `null` without one. To pass `allow_with_token` rules, send the sandbox's agent token (`agent.token`) in the `X-Sandbox-Token` header.

```json
"experimental": {
  "network_policy": {
    "inbound": [{ "to_port": "80", "from": ["10.0.0.0/8"], "access": "allow" }]
  }
}
```

### How a request is decided

There is no precedence to learn: **a port has at most one rule, and at most one rule is `"*"`**. A request to a port is decided by:

1. that port's rule, if the client is in its `from`;
2. otherwise the `"*"` rule, if the client is in its `from`;
3. otherwise the request is allowed.

Also:

- `X-Sandbox-Token` is always removed before the request reaches the sandbox.
- The agent port (57468, used by the SDKs) can be narrowed but never closed by accident: only a rule naming that port alone applies to it, never the `"*"` rule or a range. If that rule is `allow` or `allow_with_token`, clients outside its `from` are denied.
- An invalid policy (two rules for one port, overlapping ranges, more than one `"*"` rule, a bad IP or CIDR) is rejected when the sandbox is created.

### Examples

TypeScript:

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
  experimental: {
    network_policy: {
      inbound: [
        { to_port: "80", from: ["10.0.0.0/8"], access: "allow" },
        { to_port: "3000", from: ["*"], access: "allow_with_token" },
        { to_port: "*", from: ["*"], access: "deny" },
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
            "inbound": [
                {"to_port": "80", "from": ["10.0.0.0/8"], "access": "allow"},
                {"to_port": "3000", "from": ["*"], "access": "allow_with_token"},
                {"to_port": "*", "from": ["*"], "access": "deny"},
            ]
        }
    },
)
```

CLI (`sandboxes get` shows the rules under **Experimental**):

```bash
together-sandbox sandboxes create @my-app@v1 --experimental '{
  "network_policy": {"inbound": [
    {"to_port": "80", "from": ["10.0.0.0/8"], "access": "allow"},
    {"to_port": "3000", "from": ["*"], "access": "allow_with_token"},
    {"to_port": "*", "from": ["*"], "access": "deny"}
  ]}
}'
```
