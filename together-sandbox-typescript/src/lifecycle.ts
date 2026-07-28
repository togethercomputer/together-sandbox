/**
 * Lifecycle helper — turns a non-running / non-terminated sandbox state into a
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
  status_reason?: string | null;
  statusReason?: string | null;
}

/** status_reason → hint when expecting "running" but ended up terminal. */
const STATUS_REASON_HINTS: Record<string, string> = {
  internal_error:
    "Sandbox failed to start due to an internal error. Common causes: image not found or snapshot corrupted. Try re-creating from a known-good snapshot; if it persists, report it.",
  out_of_capacity:
    "Sandbox could not be scheduled — the cluster is out of capacity. Retry shortly, or try a different cluster.",
  oom_killed:
    "Sandbox was killed for exceeding its memory limit. Increase memoryBytes when creating the sandbox.",
  crashed:
    "The VM crashed. A terminated sandbox is terminal — create a new sandbox from a known-good snapshot.",
  evicted:
    "Sandbox was evicted from its node. A terminated sandbox is terminal — create a new sandbox from a snapshot.",
  node_lost:
    "Sandbox's node was lost. A terminated sandbox is terminal — create a new sandbox from a snapshot.",
  cluster_lost:
    "Sandbox's cluster was lost. A terminated sandbox is terminal — create a new sandbox from a snapshot.",
};

/**
 * Statuses a sandbox can still move out of on its own. Any other status is
 * settled — waiting on it would return immediately, so callers can skip the
 * wait phase entirely.
 */
const TRANSIENT_STATUSES = new Set(["starting", "terminating"]);

/** True when the sandbox is still moving and a wait is worthwhile. */
export function isTransientStatus(status: string | null | undefined): boolean {
  return status != null && TRANSIENT_STATUSES.has(status);
}

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
 *   1. `status === "unrecovered"`             — crash recovery failed; create a new sandbox.
 *   2. `status === "recovering"`              — auto-recovery in progress, wait and retry.
 *   3. `status` of `starting | terminating`  — wait endpoint returned early (unexpected).
 *   4. `status === "failed_to_start"`         — never started; use `status_reason`.
 *   5. Wrong terminal (`terminated` ↔ `running`) — use `status_reason`.
 *   6. Fallthrough.
 */
export function describeLifecycleFailure(
  sandbox: LifecycleSandbox,
  expected: "running" | "terminated",
): string {
  const id = sandbox.id ?? "<unknown>";
  const status = sandbox.status ?? "<unknown>";
  const reason = firstDefined(
    sandbox.status_reason,
    sandbox.statusReason,
  );

  // 1. Unrecovered — crash recovery failed; terminal, biggest signal
  if (status === "unrecovered") {
    return (
      `Sandbox '${id}' could not be recovered ` +
      `(status: 'unrecovered'${reason ? `, status_reason: '${reason}'` : ""}).\n` +
      `Hint: this sandbox cannot be recovered — create a new sandbox from a snapshot.`
    );
  }

  // 2. Recovering — wait, do not retry blindly
  if (status === "recovering") {
    return (
      `Sandbox '${id}' is currently being auto-recovered (status: 'recovering'` +
      `${reason ? `, status_reason: '${reason}'` : ""}).\n` +
      `Hint: recovery is in progress — wait a few seconds then retry sdk.sandboxes.get('${id}'). ` +
      `If it becomes 'unrecovered' you'll need to create a new sandbox.`
    );
  }

  // 3. Transient — wait returned without reaching a terminal status
  if (isTransientStatus(status)) {
    return (
      `Sandbox '${id}' is still in transient state '${status}' after wait returned.\n` +
      `Hint: this is unexpected (waitForSandbox should only return at a terminal status). ` +
      `Retry sdk.sandboxes.get('${id}') to check progress; report if it persists.`
    );
  }

  // 4. Failed to start — never reached running
  if (expected === "running" && status === "failed_to_start") {
    const hint =
      (reason && STATUS_REASON_HINTS[reason]) ??
      `The sandbox never started — create a new sandbox from a known-good snapshot.`;
    return (
      `Sandbox '${id}' failed to start` +
      `${reason ? ` (status_reason: '${reason}')` : ""}.\nHint: ${hint}`
    );
  }

  // 5. Wrong terminal — reached the other end
  if (expected === "running" && status === "terminated") {
    const hint =
      (reason && STATUS_REASON_HINTS[reason]) ??
      `A terminated sandbox is terminal — create a new sandbox from a snapshot, or call sdk.sandboxes.get('${id}') to inspect.`;
    return (
      `Sandbox '${id}' terminated instead of reaching 'running'` +
      `${reason ? ` (status_reason: '${reason}')` : ""}.\nHint: ${hint}`
    );
  }

  if (expected === "terminated" && status === "running") {
    return (
      `Sandbox '${id}' is still running — the terminate request did not take effect.\n` +
      `Hint: retry sdk.sandboxes.terminate('${id}'); report if it persists.`
    );
  }

  // 6. Fallthrough — genuinely unexpected combination
  const extras: string[] = [];
  if (reason) extras.push(`status_reason: '${reason}'`);
  const extrasStr = extras.length > 0 ? `, ${extras.join(", ")}` : "";
  return (
    `Sandbox '${id}' reached unexpected status '${status}' (expected '${expected}'${extrasStr}).\n` +
    `Hint: call sdk.sandboxes.get('${id}') to inspect.`
  );
}
