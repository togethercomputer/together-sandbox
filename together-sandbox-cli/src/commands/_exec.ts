// Minimal client for the in-VM agent (pint) exec API, talking to it directly
// from the CLI over Node's global `fetch` / `WebSocket`. One-shot execs use the
// SSE stream (exit code arrives inline); interactive execs use the websocket
// (bidirectional stdin + PTY resize), polling for the exit code on close.

export interface ExecTarget {
  /** Agent base URL (e.g. https://host:port). */
  agent: string;
  /** Agent bearer token. */
  token: string;
}

export interface ExecSpec {
  cmd: string;
  args: string[];
  cwd?: string;
  env?: Record<string, string>;
  user?: string;
}

interface ExecItem {
  id: string;
  status: string;
  exitCode?: number;
}

/**
 * Resolve the command + args from a parsed argv, combining the variadic
 * `[command..]` positional (args before `--`) with everything after `--`
 * (yargs puts those in `argv["--"]` when `populate--` is enabled). This lets
 * both `run <ref> ls -la` and `run <ref> -- ls -la` work.
 */
export function fullCommand(argv: Record<string, unknown>): string[] {
  const pre = (argv.command as unknown[] | undefined) ?? [];
  const post = (argv["--"] as unknown[] | undefined) ?? [];
  return [...pre, ...post].map(String);
}

/** Parse repeated `KEY=VALUE` strings into an env record. */
export function parseEnv(
  pairs: string[] | undefined,
): Record<string, string> | undefined {
  if (!pairs || pairs.length === 0) return undefined;
  const env: Record<string, string> = {};
  for (const pair of pairs) {
    const eq = pair.indexOf("=");
    if (eq === -1) throw new Error(`invalid --env "${pair}" (expected KEY=VALUE)`);
    env[pair.slice(0, eq)] = pair.slice(eq + 1);
  }
  return env;
}

/**
 * Run a command in a sandbox, choosing interactive (PTY over websocket) vs
 * one-shot (SSE) based on the `-i`/`-t` flags AND whether stdin is a TTY.
 * Resolves with the command's exit code.
 */
export function runExec(
  target: ExecTarget,
  spec: ExecSpec,
  opts: { interactive?: boolean; tty?: boolean },
): Promise<number> {
  const interactive =
    Boolean(opts.tty || opts.interactive) && Boolean(process.stdin.isTTY);
  return interactive ? execInteractive(target, spec) : execOneShot(target, spec);
}

function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` };
}

async function createExec(
  target: ExecTarget,
  spec: ExecSpec,
  pty: boolean,
): Promise<ExecItem> {
  const res = await fetch(`${target.agent}/api/v1/execs`, {
    method: "POST",
    headers: { ...authHeaders(target.token), "Content-Type": "application/json" },
    body: JSON.stringify({
      command: spec.cmd,
      args: spec.args,
      autostart: true,
      pty,
      cwd: spec.cwd,
      env: spec.env,
      user: spec.user,
    }),
  });
  if (!res.ok) {
    throw new Error(`failed to create exec: HTTP ${res.status} ${await res.text()}`);
  }
  return (await res.json()) as ExecItem;
}

/**
 * Diagnostic: a plain HTTP GET to the websocket path. The agent's status code
 * pins down why an upgrade failed (401 auth, 404 path, 400 = route+auth OK but
 * not a ws request → real handshake should work / proxy issue, 2xx/5xx = proxy).
 */
async function probeUpgrade(target: ExecTarget, id: string): Promise<string> {
  try {
    const res = await fetch(
      `${target.agent}/ws/v1/execs/${id}?token=${encodeURIComponent(target.token)}`,
      { headers: authHeaders(target.token) },
    );
    const body = (await res.text()).slice(0, 200).trim();
    return `HTTP probe of /ws/v1 path → ${res.status} ${res.statusText}${body ? ` — ${body}` : ""}`;
  } catch (e) {
    return `HTTP probe failed: ${e instanceof Error ? e.message : String(e)}`;
  }
}

async function getExec(target: ExecTarget, id: string): Promise<ExecItem> {
  const res = await fetch(`${target.agent}/api/v1/execs/${id}`, {
    headers: authHeaders(target.token),
  });
  if (!res.ok) {
    throw new Error(`failed to get exec: HTTP ${res.status} ${await res.text()}`);
  }
  return (await res.json()) as ExecItem;
}

/** Read all of process.stdin to a string (used when stdin is piped). */
function readAllStdin(): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    process.stdin.on("data", (c) => chunks.push(Buffer.from(c)));
    process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    process.stdin.on("error", reject);
  });
}

/** Read piped stdin and POST it as the exec's input. Errors are swallowed. */
async function forwardStdin(target: ExecTarget, id: string): Promise<void> {
  try {
    const input = await readAllStdin();
    if (input.length === 0) return;
    await fetch(`${target.agent}/api/v1/execs/${id}/io`, {
      method: "POST",
      headers: { ...authHeaders(target.token), "Content-Type": "application/json" },
      body: JSON.stringify({ type: "stdin", input }),
    });
  } catch {
    /* stdin closed / forwarding failed — non-fatal */
  }
}

/**
 * Run a command to completion, streaming stdout/stderr to the terminal.
 * Resolves with the command's exit code.
 */
export async function execOneShot(
  target: ExecTarget,
  spec: ExecSpec,
): Promise<number> {
  const exec = await createExec(target, spec, false);

  // Forward piped stdin (only when not a TTY) concurrently — never block the
  // output/exit loop waiting on stdin EOF (which may never arrive). When the
  // command exits we return and the caller exits the process, abandoning any
  // still-pending read. pint appends a trailing newline to the input.
  if (!process.stdin.isTTY) {
    void forwardStdin(target, exec.id);
  }

  const res = await fetch(
    `${target.agent}/api/v1/stream/execs/${exec.id}/io`,
    { headers: { ...authHeaders(target.token), Accept: "text/event-stream" } },
  );
  if (!res.ok || !res.body) {
    throw new Error(`failed to stream exec output: HTTP ${res.status}`);
  }

  let exitCode = 0;
  for await (const frame of parseSse(res.body)) {
    if (frame.output) {
      if (frame.type === "stderr") process.stderr.write(frame.output);
      else process.stdout.write(frame.output);
    }
    if (typeof frame.exitCode === "number") {
      exitCode = frame.exitCode;
      break;
    }
  }
  return exitCode;
}

interface SseFrame {
  output?: string;
  type?: "stdout" | "stderr";
  sequence?: number;
  exitCode?: number;
}

/** Parse an SSE byte stream, yielding the JSON payload of each `data:` event. */
async function* parseSse(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<SseFrame> {
  const decoder = new TextDecoder();
  let buffer = "";
  // @ts-expect-error - web ReadableStream is async-iterable at runtime in Node.
  for await (const chunk of body) {
    buffer += decoder.decode(chunk, { stream: true });
    let sep: number;
    // Events are separated by a blank line.
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      for (const line of rawEvent.split("\n")) {
        if (!line.startsWith("data:")) continue; // skip `:` comments / other fields
        const data = line.slice(5).trim();
        if (!data) continue;
        try {
          yield JSON.parse(data) as SseFrame;
        } catch {
          /* ignore malformed frame */
        }
      }
    }
  }
}

/**
 * Run an interactive PTY session over the agent websocket: raw-mode stdin is
 * forwarded as input, terminal resizes are forwarded, output is written to the
 * terminal. Resolves with the command's exit code once it exits.
 */
export async function execInteractive(
  target: ExecTarget,
  spec: ExecSpec,
): Promise<number> {
  // Set TERM for the remote PTY so termcap programs (clear, vim, less, top…)
  // work, mirroring `docker exec -it`. An explicit --env TERM wins.
  const env = { TERM: process.env.TERM || "xterm-256color", ...spec.env };
  const exec = await createExec(target, { ...spec, env }, true);

  const wsUrl =
    `${target.agent.replace(/^http/, "ws")}/ws/v1/execs/${exec.id}` +
    `?token=${encodeURIComponent(target.token)}`;
  // Send an Origin matching the agent host (the ingress may reject upgrades
  // without one) and the bearer token as a header in addition to the query
  // param. The DOM `WebSocket` type omits `headers`, but Node's undici
  // implementation accepts it — cast past the lib types.
  const wsOptions = {
    headers: {
      Authorization: `Bearer ${target.token}`,
      Origin: target.agent.replace(/^http:/, "https:"),
    },
  };
  const ws = new WebSocket(wsUrl, wsOptions as unknown as string[]);

  const stdin = process.stdin;
  const wasRaw = stdin.isTTY ? stdin.isRaw : false;

  const sendResize = () => {
    if (ws.readyState !== WebSocket.OPEN) return;
    ws.send(
      JSON.stringify({
        type: "resize",
        data: {
          cols: process.stdout.columns ?? 80,
          rows: process.stdout.rows ?? 24,
        },
      }),
    );
  };
  const onStdin = (chunk: Buffer) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "input", data: { input: chunk.toString("utf8") } }));
    }
  };

  const cleanup = () => {
    process.stdout.off("resize", sendResize);
    stdin.off("data", onStdin);
    if (stdin.isTTY) stdin.setRawMode(wasRaw);
    stdin.pause();
  };

  const wsOrigin = (() => {
    try {
      return new URL(wsUrl).origin;
    } catch {
      return target.agent;
    }
  })();

  return new Promise<number>((resolve, reject) => {
    let opened = false;
    let settled = false;

    const fail = (detail: string) => {
      if (settled) return;
      settled = true;
      cleanup();
      // Probe the path over plain HTTP to capture the actual status code, then
      // reject with both the ws detail and the probe result.
      void probeUpgrade(target, exec.id).then((probe) =>
        reject(
          new Error(
            `websocket connection to sandbox agent (${wsOrigin}) failed: ${detail}\n  ${probe}`,
          ),
        ),
      );
    };

    ws.addEventListener("open", () => {
      opened = true;
      if (stdin.isTTY) stdin.setRawMode(true);
      stdin.resume();
      stdin.on("data", onStdin);
      process.stdout.on("resize", sendResize);
      sendResize();
    });

    ws.addEventListener("message", (event) => {
      let msg: { type?: string; data?: { output?: string; stream?: string; error?: string } };
      try {
        msg = JSON.parse(typeof event.data === "string" ? event.data : String(event.data));
      } catch {
        return;
      }
      if (msg.type === "output" && msg.data?.output) {
        if (msg.data.stream === "stderr") process.stderr.write(msg.data.output);
        else process.stdout.write(msg.data.output);
      } else if (msg.type === "error" && msg.data?.error) {
        process.stderr.write(`${msg.data.error}\n`);
      }
    });

    const finish = async () => {
      if (settled) return;
      settled = true;
      cleanup();
      try {
        const final = await getExec(target, exec.id);
        resolve(typeof final.exitCode === "number" && final.exitCode >= 0 ? final.exitCode : 0);
      } catch {
        resolve(0);
      }
    };

    ws.addEventListener("close", (event) => {
      // Closing before the socket ever opened means the upgrade was rejected
      // (bad token, proxy not forwarding the upgrade, etc.) — surface it as an
      // error rather than a silent exit 0.
      if (!opened) {
        const code = (event as { code?: number }).code;
        const reason = (event as { reason?: string }).reason;
        fail(
          `connection closed before opening` +
            (code ? ` (code ${code}${reason ? `: ${reason}` : ""})` : ""),
        );
        return;
      }
      void finish();
    });
    ws.addEventListener("error", (event) => {
      const detail =
        (event as { message?: string }).message ||
        (event as { error?: { message?: string; code?: string } }).error?.message ||
        (event as { error?: { code?: string } }).error?.code ||
        "unknown error";
      fail(String(detail));
    });

    // Detect process exit: the agent keeps the ws open after exit, so poll
    // status and close the socket ourselves once the command has finished.
    const poll = setInterval(async () => {
      try {
        const item = await getExec(target, exec.id);
        if (item.status === "EXITED" || item.status === "STOPPED") {
          clearInterval(poll);
          ws.close();
        }
      } catch {
        clearInterval(poll);
        ws.close();
      }
    }, 500);
  });
}
