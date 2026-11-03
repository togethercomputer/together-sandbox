import asyncio
import hashlib
import json
import os
import re
import secrets
import shlex
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from together_sandbox import (
    CreateContextSnapshotParams,
    HttpError,
    SnapshotProgress,
    TogetherSandbox,
)

# Which agent to run (`hermes` or `openclaw`) and which Together model it uses.
AGENT = os.environ.get("AGENT", "hermes")
MODEL = os.environ.get("MODEL", "MiniMaxAI/MiniMax-M3")
# Leave the agent's gateway running instead of a one-shot prompt + teardown.
KEEP_RUNNING = os.environ.get("KEEP_RUNNING") == "1"
# Set up a sandbox and print the CLI commands to chat with the agent yourself.
INTERACTIVE = os.environ.get("INTERACTIVE") == "1"
# Start the agent's web UI and print its URL and login.
WEB = os.environ.get("WEB") == "1"
# Print a fresh one-time OpenClaw sign-in link for this running sandbox.
LINK = os.environ.get("LINK")
# Sandboxes left running for you terminate themselves after this.
TTL_SECONDS = 2 * 60 * 60

# Where the agent sends model calls. Override to use a non-production Together
# environment (e.g. QA), whose inference API may need its own key.
INFERENCE_BASE_URL = os.environ.get(
    "INFERENCE_BASE_URL", "https://api.together.xyz/v1"
)
PROMPT = "Reply with one short sentence saying which model you are."


def hermes_config(web_url: str | None) -> str:
    # Hermes expands ${OPENAI_API_KEY} from the exec's environment, so the key
    # is never written to disk. Without api_key, a custom provider does not
    # fall back to the env var: it sends the placeholder `no-key-required`.
    return f"""model:
  default: {MODEL}
  provider: custom
  base_url: {INFERENCE_BASE_URL}
  api_key: ${{OPENAI_API_KEY}}
"""


def openclaw_config(web_url: str | None) -> str:
    config = {
        "gateway": {"mode": "local"},
        "agents": {"defaults": {"model": {"primary": f"together/{MODEL}"}}},
        # Without a search provider OpenClaw has no web_search tool, and falls
        # back to guessing URLs. DuckDuckGo needs no API key, but is a plugin
        # (installed in the image) and is never picked automatically.
        "tools": {"web": {"search": {"provider": "duckduckgo"}}},
        "plugins": {
            "entries": {
                "duckduckgo": {
                    "enabled": True,
                    "config": {"webSearch": {"region": "de-de"}},
                }
            }
        },
        # Chromium from the image, for the browser tool. Its own sandbox can't
        # start inside the sandbox, which already isolates it.
        "browser": {
            "executablePath": "/usr/bin/chromium",
            "headless": True,
            "noSandbox": True,
        },
        # OpenClaw's bundled `together` provider only knows a few models, so
        # register this one. Merged into the bundled provider, not replacing it.
        "models": {
            "mode": "merge",
            "providers": {
                "together": {
                    "baseUrl": INFERENCE_BASE_URL,
                    # Substituted from the exec's environment when OpenClaw
                    # loads the config, so the key is never written to disk.
                    "apiKey": "${TOGETHER_API_KEY}",
                    "api": "openai-completions",
                    "models": [
                        {
                            "id": MODEL,
                            "name": MODEL,
                            "compat": {"supportsUsageInStreaming": True},
                        }
                    ],
                }
            },
        },
    }
    if web_url:
        config["gateway"].update(
            {
                "port": AGENTS["openclaw"]["web_port"],
                # Listen on all interfaces, so the sandbox's public URL reaches it.
                "bind": "lan",
                # A public bind requires a login; the password is passed as
                # OPENCLAW_GATEWAY_PASSWORD, so it isn't written to disk.
                "auth": {"mode": "password"},
                # Browsers may only connect from allowed origins.
                "controlUi": {"allowedOrigins": [web_url]},
                # Requests arrive through the sandbox's proxies, from internal
                # 10.x addresses. Without this, OpenClaw rejects them as
                # unattributed proxy traffic.
                "trustedProxies": ["10.0.0.0/8"],
            }
        )
    return json.dumps(config, indent=2)


# Each agent runs as the uid-1000 user from its templates/<agent>/Dockerfile.
# The user must be passed explicitly: an exec without one runs as the
# sandbox's default user, which is root for these images.
AGENTS = {
    "hermes": {
        "user": "ubuntu",
        "home": "/home/ubuntu",
        "config_path": ".hermes/config.yaml",
        "config": hermes_config,
        "smoke": ["hermes", "chat", "-q", PROMPT],
        "serve": ["hermes", "gateway", "run"],
        "chat": ["hermes"],
        "key_var": "OPENAI_API_KEY",
        "web_port": 9119,
    },
    "openclaw": {
        "user": "node",
        "home": "/home/node",
        "config_path": ".openclaw/openclaw.json",
        "config": openclaw_config,
        "smoke": ["openclaw", "agent", "exec", PROMPT],
        "serve": ["openclaw", "gateway", "run"],
        # A shell, from which you can run `openclaw` commands.
        "chat": ["bash"],
        "key_var": "TOGETHER_API_KEY",
        "web_port": 18789,
    },
}


def on_progress(p: SnapshotProgress) -> None:
    """Called for each build step: prepare, build, push, register, alias."""
    print(f"  [{p.step}] {p.output}")


def snapshot_alias() -> str:
    # Keyed on the Dockerfile's contents, so editing it builds a new snapshot
    # instead of reusing one built from an older version.
    dockerfile = Path(__file__).parent / "templates" / AGENT / "Dockerfile"
    digest = hashlib.sha256(dockerfile.read_bytes()).hexdigest()[:12]
    return f"{AGENT}-agent-{digest}"


async def get_or_build_snapshot(sdk: TogetherSandbox, alias: str) -> str:
    try:
        # A 404 here just means the snapshot has not been built yet.
        existing = await sdk.snapshots.get_by_alias(alias)
        print(f"Reusing existing snapshot: id={existing.id} alias={alias}")
        return str(existing.id)
    except HttpError as e:
        if e.status != 404:
            raise

    # The agent is installed at build time, so sandboxes start with it ready.
    context = Path(__file__).parent / "templates" / AGENT
    print(f"Snapshot not found, building from ./templates/{AGENT}/Dockerfile ...")
    result = await sdk.snapshots.create(
        CreateContextSnapshotParams(
            context=str(context),
            alias=alias,
            on_progress=on_progress,
        )
    )
    print(f"Snapshot created: id={result.snapshot_id} alias={result.alias}")
    return result.snapshot_id


async def run_cmd(sandbox, cmd: list[str], *, user: str, home: str, env: dict) -> dict:
    # Commands go through `bash -c` because the sandbox looks up the program
    # itself in its own PATH, not the one in `env`, so it can't find `hermes`
    # directly. bash (in /usr/bin) then uses env's PATH. Not a login shell, so
    # /etc/profile doesn't override it.
    return await sandbox.execs.exec(
        "bash", ["-c", shlex.join(cmd)], cwd=home, env=env, user=user
    )


# ─── Web UI ──────────────────────────────────────────────────────────────────


def port_url(sandbox, port: int) -> str:
    """Each sandbox port is served at the agent URL with the port swapped in."""
    agent_url = sandbox.vm_info.agent.url or ""
    url = re.sub(r"-\d+\.sandbox\.", f"-{port}.sandbox.", agent_url, count=1)
    if url == agent_url:
        raise RuntimeError(f"Unexpected sandbox URL format: {agent_url!r}")
    return url


def http_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            return res.status
    except urllib.error.HTTPError as e:
        return e.code
    except OSError:
        return 0


async def wait_until_reachable(url: str, timeout: float = 120) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        # Any answer from the app, even a login page, means it is up. The
        # sandbox proxy answers 502 until something listens on the port.
        if 0 < await asyncio.to_thread(http_status, url) < 500:
            return
        await asyncio.sleep(2)
    raise RuntimeError(f"{url} did not start in time")


async def openclaw_link(sandbox, url: str, **run_opts) -> str:
    """
    A one-time link that signs a browser in as the owner. Logging in with the
    password alone still leaves a new browser waiting for pairing approval.
    """
    for _ in range(10):
        result = await run_cmd(sandbox, ["openclaw", "dashboard", "--json"], **run_opts)
        match = re.search(r"\{.*\}", result["output"], re.S)
        info = json.loads(match.group(0)) if match else {}
        if info.get("ok"):
            break
        await asyncio.sleep(3)  # The gateway is still starting.
    else:
        raise RuntimeError(f"openclaw dashboard failed: {result['output'][-500:]}")
    # The link points at 127.0.0.1 inside the sandbox. Keep its one-time
    # fragment, but point the page and its websocket at the public URL.
    fragment = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(info["browserUrl"]).fragment))
    fragment["gatewayUrl"] = url.replace("https://", "wss://", 1)
    return f"{url}/#{urllib.parse.urlencode(fragment)}"


async def start_web(sandbox, url: str, **run_opts) -> dict[str, str]:
    """Start the agent's web UI as a background exec and return its login."""
    password = secrets.token_urlsafe(18)
    port = str(AGENTS[AGENT]["web_port"])
    if AGENT == "hermes":
        cmd = ["hermes", "dashboard", "--host", "0.0.0.0", "--port", port,
               "--skip-build", "--no-open"]
        extra_env = {
            "HERMES_DASHBOARD_BASIC_AUTH_USERNAME": "admin",
            "HERMES_DASHBOARD_BASIC_AUTH_PASSWORD": password,
            "HERMES_DASHBOARD_PUBLIC_URL": url,
        }
    else:
        cmd = ["openclaw", "gateway", "run"]
        extra_env = {"OPENCLAW_GATEWAY_PASSWORD": password}
    await sandbox.execs.create(
        "bash",
        ["-c", shlex.join(cmd)],
        autostart=True,
        cwd=run_opts["home"],
        env={**run_opts["env"], **extra_env},
        user=run_opts["user"],
    )
    await wait_until_reachable(url)
    if AGENT == "hermes":
        return {"Username": "admin", "Password": password}
    return {
        "Password": password,
        "Sign-in link (one-time, 10 minutes)": await openclaw_link(sandbox, url, **run_opts),
    }


async def main() -> None:
    if AGENT not in AGENTS:
        raise SystemExit(f"AGENT must be one of {sorted(AGENTS)}, got {AGENT!r}")
    agent = AGENTS[AGENT]
    user = agent["user"]
    home = agent["home"]
    # The sandbox API always uses TOGETHER_API_KEY; the agent's model calls
    # can use a different key, e.g. for a QA inference environment.
    api_key = os.environ.get("INFERENCE_API_KEY") or os.environ["TOGETHER_API_KEY"]

    # Execs get exactly this environment.
    env = {
        "HOME": home,
        "PATH": f"{home}/.local/bin:/usr/local/bin:/usr/bin:/bin",
        "TOGETHER_API_KEY": api_key,
        "OPENAI_API_KEY": api_key,
    }
    # A bare user name sets only the uid; the group would stay root's.
    run_opts = {"user": f"{user}:{user}", "home": home, "env": env}

    async def run(cmd: list[str], as_user: str = run_opts["user"]) -> dict:
        return await run_cmd(sandbox, cmd, **{**run_opts, "user": as_user})

    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from the environment

    if LINK:
        if AGENT != "openclaw":
            raise SystemExit("LINK only applies to AGENT=openclaw.")
        sandbox = await sdk.sandboxes.connect(LINK)
        url = port_url(sandbox, agent["web_port"])
        print(f"Sign-in link (one-time, 10 minutes):\n  {await openclaw_link(sandbox, url, **run_opts)}")
        await sandbox.close()
        return

    snapshot_id = await get_or_build_snapshot(sdk, snapshot_alias())

    print("Creating sandbox from snapshot (it starts automatically)...")
    sandbox = await sdk.sandboxes.create(
        snapshot_id=snapshot_id,
        cpu=2,
        memory_bytes=4 * 1024**3,
        ttl=TTL_SECONDS if INTERACTIVE or WEB else None,
        tags={"agent": AGENT},
    )
    print(f"Sandbox running: {sandbox.id}")

    try:
        # Sandboxes start with an empty hostname. OpenClaw's gateway records
        # the hostname with its state lock, and refuses to start without one.
        await run(["hostname", f"{AGENT}-sandbox"], as_user="root")

        # Write the agent's config. The installer may already have created
        # this file, so remove it first and write a fresh one.
        web_url = port_url(sandbox, agent["web_port"]) if WEB else None
        config_path = f"{home}/{agent['config_path']}"
        await run(["mkdir", "-p", os.path.dirname(config_path)])
        await run(["rm", "-f", config_path])
        await sandbox.files.create(config_path, agent["config"](web_url))
        # Files are written as the sandbox's own (root) user. Hand the config
        # directory to the agent's user: Hermes refuses to use a home it
        # doesn't own, or one with files it can't write.
        await run(
            ["chown", "-R", f"{user}:{user}", os.path.dirname(config_path)],
            as_user="root",
        )
        print(f"Wrote {config_path} (model: {MODEL})")

        if INTERACTIVE:
            # The CLI's `-it` attaches your terminal to the agent, which this
            # script can't do. The key is read from your local shell when you
            # run the command, so it isn't printed here.
            key_ref = '"${INFERENCE_API_KEY:-$TOGETHER_API_KEY}"'
            print_env = {k: v for k, v in env.items() if not k.endswith("API_KEY")}
            flags = " ".join(f"--env {k}={shlex.quote(v)}" for k, v in print_env.items())
            # PTY execs (what `-it` uses) ignore the requested user and run as
            # root, so switch to the agent's user inside the exec instead.
            # setpriv keeps the environment, unlike `su`.
            chat = [
                "setpriv", f"--reuid={user}", f"--regid={user}", "--init-groups",
                "bash", "-c", shlex.join(agent["chat"]),
            ]
            print(
                f"\nSandbox ready. It terminates itself in "
                f"{TTL_SECONDS // 3600}h if you don't.\n\n"
                f"Chat with {AGENT}:\n"
                f"  together-sandbox sandbox exec run {sandbox.id} -it "
                f"--cwd {home} {flags} "
                f"--env {agent['key_var']}={key_ref} -- {shlex.join(chat)}\n\n"
                f"Close the sandbox when you're done:\n"
                f"  together-sandbox sandboxes terminate {sandbox.id}"
            )
            return

        if WEB:
            print(f"Starting the {AGENT} web UI...")
            login = await start_web(sandbox, web_url, **run_opts)
            print(f"\n{AGENT} web UI: {web_url}")
            for label, value in login.items():
                print(f"  {label}: {value}")
            if AGENT == "openclaw":
                print(
                    "\nOpen the sign-in link to connect this browser. For another "
                    "browser, or after it expires, get a new one with:\n"
                    f"  LINK={sandbox.id} AGENT=openclaw uv run start_agent.py"
                )
            print(
                f"\nThe sandbox terminates itself in {TTL_SECONDS // 3600}h. "
                f"Close it sooner with:\n"
                f"  together-sandbox sandboxes terminate {sandbox.id}"
            )
            return

        if not KEEP_RUNNING:
            print(f"Sending a test prompt to {AGENT}...")
            result = await run(agent["smoke"])
            print(f"exit code {result['exit_code']}:\n{result['output']}")
            return

        # Start the gateway as a background exec. It keeps running after this
        # script exits, until the exec or the sandbox is stopped.
        serve = await sandbox.execs.create(
            "bash",
            ["-c", shlex.join(agent["serve"])],
            autostart=True,
            cwd=home,
            env=env,
            user=run_opts["user"],
        )
        print(f"Started {AGENT} gateway as exec {serve.id}. First 30s of logs:")
        try:
            async with asyncio.timeout(30):
                async for event in sandbox.execs.stream_output(serve.id):
                    print(event.get("output", ""), end="")
        except TimeoutError:
            pass
        print(f"\nLeft running. Terminate with: sdk.sandboxes.terminate({sandbox.id!r})")
    finally:
        # Terminate in a `finally` so a failure above still cleans up — a
        # sandbox runs until you stop it. Created without a termination
        # policy, so it is ephemeral: no snapshot is kept.
        if not (KEEP_RUNNING or INTERACTIVE or WEB):
            print("Terminating sandbox...")
            await sdk.sandboxes.terminate(sandbox.id)
            print("Done.")
        await sandbox.close()


asyncio.run(main())
