# run-agent-python-sdk

Example of using the [Together Sandbox Python SDK](https://pypi.org/project/together-sandbox/) to run an AI agent — [Hermes Agent](https://github.com/NousResearch/hermes-agent) or [OpenClaw](https://openclaw.ai) — in a sandbox, with the agent's model served by Together. Uses `together-sandbox >= 4.0.1` from PyPI.

## What it does

1. Looks for a snapshot aliased `<agent>-agent-<hash of its Dockerfile>`. If
   not found, builds one remotely from `templates/<agent>/Dockerfile`, which
   installs the agent. Editing a Dockerfile therefore triggers a fresh build.
2. Creates a sandbox from the snapshot (it starts automatically).
3. Writes the agent's config file, pointing it at `MODEL` on Together's
   OpenAI-compatible API:
   - Hermes: `~/.hermes/config.yaml`
   - OpenClaw: `~/.openclaw/openclaw.json`
4. Then, depending on the mode:
   - **default:** sends one test prompt, prints the reply, and terminates the sandbox
   - **`WEB=1`:** starts the agent's web UI and prints its URL and login (see below)
   - **`INTERACTIVE=1`:** prints a CLI command to chat with the agent in your terminal
   - **`KEEP_RUNNING=1`:** starts the agent's messaging gateway

The API key is passed to the agent as an environment variable on each exec,
never written into the config file, so it does not end up in snapshots.

## Structure

```
templates/hermes/Dockerfile     # Image with Hermes Agent installed
templates/openclaw/Dockerfile   # Image with OpenClaw installed
start_agent.py                  # Main script — agent configs and commands live at the top
```

## Setup

```bash
# Install dependencies
uv sync

# Required — used both for the sandbox API and for the agent's model calls
export TOGETHER_API_KEY="your-key-here"

# Optional
export AGENT="openclaw"                       # default: hermes
export MODEL="zai-org/GLM-5.3-Flash"          # any Together model ID; default: MiniMaxAI/MiniMax-M3
export WEB=1                                  # start the agent's web UI and leave the sandbox running

# Optional — non-production environments
export TOGETHER_BASE_URL="https://..."        # sandbox management API (SDK default: production)
export INFERENCE_BASE_URL="https://api.qa.together.ai/v1"  # where the agent sends model calls (QA shown); default: https://api.together.xyz/v1
export INFERENCE_API_KEY="..."                # key for those model calls; default: TOGETHER_API_KEY
```

## Run

```bash
uv run start_agent.py
```

The snapshot is only built on the first run for each agent (and again after
its Dockerfile changes). To change the
model, set `MODEL` and run again — only the config file changes, not the image.

## Open the agent in your browser

`WEB=1` starts the agent's web UI, leaves the sandbox running, and prints the
URL and a login. The sandbox terminates itself after 2 hours.

```bash
AGENT=hermes   WEB=1 uv run start_agent.py   # Hermes dashboard, port 9119: username + password
AGENT=openclaw WEB=1 uv run start_agent.py   # OpenClaw Control UI, port 18789: one-time sign-in link
```

OpenClaw only accepts a new browser after a one-time approval ("pairing"), even
with the right password, so the script also prints a **sign-in link** that
signs that browser in and approves it. The link works once and expires after
10 minutes. Get a new one, for another browser or after it expires, with:

```bash
LINK=<sandbox-id> AGENT=openclaw uv run start_agent.py
```

Anyone with the login (or a sign-in link) controls the agent, including its
terminal and files, and can read the API key it uses. Prefer a separate,
spend-limited `INFERENCE_API_KEY`, and terminate the sandbox when you're done.

### What OpenClaw needs in a sandbox

Besides the usual run-as-the-image's-user setup, OpenClaw needs a few things
that `start_agent.py` handles:

- **A hostname.** Sandboxes start with an empty one. OpenClaw's gateway records
  the hostname with its state lock and refuses to start without one ("cannot
  verify Gateway ownership"), so the script sets it as root first.
- **Web search and a browser.** Without a search provider OpenClaw has no
  `web_search` tool and falls back to guessing URLs. The image installs the
  key-free DuckDuckGo plugin, and the config selects it (with German results,
  `region: "de-de"`; change it in `openclaw_config`). The image also installs
  Debian's Chromium for the browser tool.
- **The model registered.** OpenClaw's bundled `together` provider only knows a
  few models, so the config adds `MODEL` to it under `models.providers.together`.
- **Gateway settings for the public URL** (web mode only): `bind: "lan"`,
  password auth, the URL in `controlUi.allowedOrigins`, and
  `trustedProxies: ["10.0.0.0/8"]`. Requests arrive through the sandbox's
  proxies from internal 10.x addresses; without that, OpenClaw rejects them as
  unattributed proxy traffic.

## Chat with the agent yourself

`INTERACTIVE=1` sets up a sandbox with the agent configured, leaves it running,
and prints two commands for the [`together-sandbox` CLI](../../docs/cli.md):
one that opens the agent in your terminal, and one that terminates the sandbox.
The sandbox also terminates itself after 2 hours.

```bash
# Install the CLI once
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash

INTERACTIVE=1 uv run start_agent.py
# → copy-paste the printed "Chat with hermes" command; exit Hermes with /exit or Ctrl+D
# → then run the printed "terminate" command
```

The printed chat command reads the API key from your local shell
(`$INFERENCE_API_KEY`, else `$TOGETHER_API_KEY`), so run it where `.env` is
loaded.

The Hermes image includes Chromium, so its browser tools work out of the box.

With `KEEP_RUNNING=1` the sandbox keeps running (and billing) until you
terminate it. Messaging channels (Telegram, Slack, …) still need to be
configured in each agent's config before the gateway is useful.
