/**
 * Lifecycle helper — turns a non-running / non-stopped sandbox state into a
 * single actionable error message.
 *
 * Mirrors `together_sandbox._lifecycle.describe_lifecycle_failure` (Python).
 */

/**
 * Minimal duck-typed shape needed to describe a lifecycle failure.
 * Accepts both raw snake_case (from the generated client) and camelCase
 * (from {@link import("./utils.js").camelCaseKeys}).
 */
export interface LifecycleSandbox {
  id?: string | null;
  status?: string | null;
  stop_reason?: string | null;
  recovery_status?: string | null;
  stopReason?: string | null;
  recoveryStatus?: string | null;
}

/** stop_reason → recovery hint when expecting "running" but ended up "stopped". */
const STOP_REASON_HINTS: Record<string, string> = {
  start_failed:
    "Sandbox failed to start. Common causes: image not found, snapshot corrupted, or cluster at capacity. Try re-creating from a known-good snapshot.",
  oom_killed:
    "Sandbox was killed for exceeding its memory limit. Increase memoryBytes when creating the sandbox.",
  crashed:
    "The VM crashed. Inspect sandbox logs and re-start, or re-create from a known-good snapshot.",
  evicted: "Sandbox was evicted from its node. Usually transient — retry sdk.sandboxes.start().",
  node_lost: "Sandbox's node was lost. Usually transient — retry sdk.sandboxes.start().",
  cluster_lost: "Sandbox's cluster was lost. Usually transient — retry sdk.sandboxes.start().",
};

function firstDefined<T>(...values: (T | null | undefined)[]): T | undefined {
  for (const v of values) {
    if (v !== null && v !== undefined) return v;
  }
  return undefined;
}

/**
 * Build a human-readable explanation of why a sandbox did not reach the
 * expected terminal state, with an actionable recovery hint.
 *
 * Order of precedence:
 *   1. `recovery_status === "unrecoverable"` — overrides everything; create a new sandbox.
 *   2. `recovery_status === "pending"`       — auto-recovery in progress, wait and retry.
 *   3. `status` of `starting | stopping`     — wait endpoint returned early (unexpected).
 *   4. `status === "created"`                — request never took effect.
 *   5. Wrong terminal (`stopped` ↔ `running`) — use `stop_reason`.
 *   6. Fallthrough.
 */
export function describeLifecycleFailure(
  sandbox: LifecycleSandbox,
  expected: "running" | "stopped",
): string {
  const id = sandbox.id ?? "<unknown>";
  const status = sandbox.status ?? "<unknown>";
  const reason = firstDefined(sandbox.stop_reason, sandbox.stopReason);
  const recovery = firstDefined(sandbox.recovery_status, sandbox.recoveryStatus);

  // 1. Unrecoverable — terminal, biggest signal
  if (recovery === "unrecoverable") {
    return (
      `Sandbox '${id}' is marked unrecoverable ` +
      `(status: '${status}'${reason ? `, stop_reason: '${reason}'` : ""}).\n` +
      `Hint: this sandbox cannot be recovered — create a new sandbox from a snapshot.`
    );
  }

  // 2. Pending recovery — wait, do not retry blindly
  if (recovery === "pending") {
    return (
      `Sandbox '${id}' is currently being auto-recovered ` +
      `(status: '${status}', recovery_status: 'pending'` +
      `${reason ? `, stop_reason: '${reason}'` : ""}).\n` +
      `Hint: recovery is in progress — wait a few seconds then retry sdk.sandboxes.get('${id}'). ` +
      `If recovery succeeds the sandbox will return to 'running' on its own; ` +
      `if it becomes 'unrecoverable' you'll need to create a new sandbox.`
    );
  }

  // 3. Transient — wait returned without reaching a terminal status
  if (status === "starting" || status === "stopping") {
    return (
      `Sandbox '${id}' is still in transient state '${status}' after wait returned.\n` +
      `Hint: this is unexpected (waitForSandbox should only return at a terminal status). ` +
      `Retry sdk.sandboxes.get('${id}') to check progress; report if it persists.`
    );
  }

  // 4. Request never took effect
  if (status === "created") {
    const method = expected === "running" ? "start" : "shutdown";
    const verb = expected === "running" ? "start" : "stop";
    return (
      `Sandbox '${id}' is still in 'created' state — the ${verb} request did not take effect.\n` +
      `Hint: retry sdk.sandboxes.${method}('${id}').`
    );
  }

  // 5. Wrong terminal — reached the other end
  if (expected === "running" && status === "stopped") {
    const hint =
      (reason && STOP_REASON_HINTS[reason]) ??
      `Retry sdk.sandboxes.start('${id}'), or call sdk.sandboxes.get('${id}') to inspect.`;
    return (
      `Sandbox '${id}' stopped instead of reaching 'running'` +
      `${reason ? ` (stop_reason: '${reason}')` : ""}.\nHint: ${hint}`
    );
  }

  if (expected === "stopped" && status === "running") {
    return (
      `Sandbox '${id}' is still running — the stop request did not take effect.\n` +
      `Hint: retry sdk.sandboxes.shutdown('${id}'); report if it persists.`
    );
  }

  // 6. Fallthrough — genuinely unexpected combination
  const extras: string[] = [];
  if (reason) extras.push(`stop_reason: '${reason}'`);
  if (recovery) extras.push(`recovery_status: '${recovery}'`);
  const extrasStr = extras.length > 0 ? `, ${extras.join(", ")}` : "";
  return (
    `Sandbox '${id}' reached unexpected status '${status}' (expected '${expected}'${extrasStr}).\n` +
    `Hint: call sdk.sandboxes.get('${id}') to inspect.`
  );
}
