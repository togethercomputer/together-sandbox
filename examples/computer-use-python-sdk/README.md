# computer-use-python-sdk

Example of using the [Together Sandbox Python SDK](https://pypi.org/project/together-sandbox/) to start a sandbox running a full Linux desktop (XFCE + Firefox) that you open in your browser. Uses `together-sandbox >= 4.0.1` from PyPI.

## What it does

1. Looks for an existing snapshot by alias (`TOGETHER_SNAPSHOT_ALIAS`, default `computer-use-example-v1`).
2. If not found, builds one remotely from `template/Dockerfile`. This image has an XFCE desktop, Firefox ESR, a terminal, and [noVNC](https://novnc.com).
3. Creates a sandbox from the snapshot (2 vCPU, 4 GB RAM, 1 hour TTL).
4. Starts the desktop with `template/start-desktop.sh`, which serves noVNC over HTTP on port 6080.
5. Prints the public URL for port 6080, plus a randomly generated VNC password.
6. When you press Ctrl+C, terminates the sandbox. It is ephemeral, so no snapshot is kept.

## Structure

```
template/Dockerfile         # Desktop image — add packages here
template/start-desktop.sh   # Starts Xvfb, XFCE, x11vnc and noVNC (port 6080)
start_desktop.py            # Main script
```

## Setup

```bash
# Install dependencies
uv sync

# Required
export TOGETHER_API_KEY="your-key-here"

# Optional
export TOGETHER_SNAPSHOT_ALIAS="my-desktop"   # snapshot alias (default: computer-use-example-v1)
export TOGETHER_SANDBOX_TTL=7200              # auto-terminate after N seconds (default: 3600)
export DESKTOP_RESOLUTION=1920x1080           # initial screen size (default: 1280x800)
```

## Run

```bash
uv run start_desktop.py
```

Example output:

```
Desktop is ready. Open it in your browser:
  https://<sandbox-id>-6080.sandbox.<cluster>.csb.app/vnc.html?autoconnect=1&resize=remote&password=...
```

The snapshot is only built on the first run, which takes a few minutes. Later runs reuse it. After you edit anything in `template/`, change `TOGETHER_SNAPSHOT_ALIAS` so the snapshot is rebuilt.

> **Note:** Anyone with the port URL can reach the noVNC page. The VNC password is the only thing protecting the desktop, so don't share the full link, because it includes the password.
