"""Lifecycle helper — turns a non-running / non-stopped sandbox state into a
single actionable error message.

Mirrors ``together-sandbox-typescript/src/lifecycle.ts``.
"""

from __future__ import annotations

from typing import Any, Literal

# stop_reason → recovery hint when expecting "running" but ended up "stopped".
_STOP_REASON_HINTS: dict[str, str] = {
    "start_failed": (
        "Sandbox failed to start. Common causes: image not found, snapshot "
        "corrupted, or cluster at capacity. Try re-creating from a "
        "known-good snapshot."
    ),
    "oom_killed": (
        "Sandbox was killed for exceeding its memory limit. Increase "
        "memory_bytes when creating the sandbox."
    ),
    "crashed": (
        "The VM crashed. Inspect sandbox logs and re-start, or re-create "
        "from a known-good snapshot."
    ),
    "evicted": (
        "Sandbox was evicted from its node. Usually transient — retry "
        "sdk.sandboxes.start()."
    ),
    "node_lost": (
        "Sandbox's node was lost. Usually transient — retry " "sdk.sandboxes.start()."
    ),
    "cluster_lost": (
        "Sandbox's cluster was lost. Usually transient — retry "
        "sdk.sandboxes.start()."
    ),
}


def _unwrap(value: Any) -> Any:
    """Normalise enum-like values to their underlying string."""
    if value is None:
        return None
    return getattr(value, "value", value)


def describe_lifecycle_failure(
    sandbox: Any,
    expected: Literal["running", "stopped"],
) -> str:
    """Return a human-readable explanation + hint for why ``sandbox`` did not
    reach ``expected``.

    Order of precedence:
      1. ``recovery_status == "unrecoverable"`` — overrides everything.
      2. ``recovery_status == "pending"``       — auto-recovery in progress.
      3. ``status`` in ``starting | stopping`` — wait endpoint returned early.
      4. ``status == "created"``               — request never took effect.
      5. Wrong terminal (``stopped`` ↔ ``running``) — use ``stop_reason``.
      6. Fallthrough.

    The ``sandbox`` argument is duck-typed: any object with the attributes
    ``id``, ``status``, ``stop_reason``, ``recovery_status`` will work.
    Enum-valued fields are unwrapped to their underlying ``.value``.
    """
    sandbox_id = getattr(sandbox, "id", None) or "<unknown>"
    status = _unwrap(getattr(sandbox, "status", None)) or "<unknown>"
    reason = _unwrap(getattr(sandbox, "stop_reason", None))
    recovery = _unwrap(getattr(sandbox, "recovery_status", None))

    # 1. Unrecoverable — terminal, biggest signal
    if recovery == "unrecoverable":
        reason_bit = f", stop_reason: '{reason}'" if reason else ""
        return (
            f"Sandbox '{sandbox_id}' is marked unrecoverable "
            f"(status: '{status}'{reason_bit}).\n"
            f"Hint: this sandbox cannot be recovered — create a new sandbox "
            f"from a snapshot."
        )

    # 2. Pending recovery — wait, do not retry blindly
    if recovery == "pending":
        reason_bit = f", stop_reason: '{reason}'" if reason else ""
        return (
            f"Sandbox '{sandbox_id}' is currently being auto-recovered "
            f"(status: '{status}', recovery_status: 'pending'{reason_bit}).\n"
            f"Hint: recovery is in progress — wait a few seconds then retry "
            f"sdk.sandboxes.get('{sandbox_id}'). If recovery succeeds the "
            f"sandbox will return to 'running' on its own; if it becomes "
            f"'unrecoverable' you'll need to create a new sandbox."
        )

    # 3. Transient — wait returned without reaching a terminal status
    if status in ("starting", "stopping"):
        return (
            f"Sandbox '{sandbox_id}' is still in transient state '{status}' "
            f"after wait returned.\n"
            f"Hint: this is unexpected (wait_for_sandbox should only return "
            f"at a terminal status). Retry sdk.sandboxes.get('{sandbox_id}') "
            f"to check progress; report if it persists."
        )

    # 4. Request never took effect
    if status == "created":
        verb = "start" if expected == "running" else "stop"
        method = "start" if expected == "running" else "shutdown"
        return (
            f"Sandbox '{sandbox_id}' is still in 'created' state — the {verb} "
            f"request did not take effect.\n"
            f"Hint: retry sdk.sandboxes.{method}('{sandbox_id}')."
        )

    # 5. Wrong terminal — reached the other end
    if expected == "running" and status == "stopped":
        hint = _STOP_REASON_HINTS.get(reason or "") or (
            f"Retry sdk.sandboxes.start('{sandbox_id}'), or call "
            f"sdk.sandboxes.get('{sandbox_id}') to inspect."
        )
        reason_bit = f" (stop_reason: '{reason}')" if reason else ""
        return (
            f"Sandbox '{sandbox_id}' stopped instead of reaching 'running'"
            f"{reason_bit}.\nHint: {hint}"
        )

    if expected == "stopped" and status == "running":
        return (
            f"Sandbox '{sandbox_id}' is still running — the stop request did "
            f"not take effect.\n"
            f"Hint: retry sdk.sandboxes.shutdown('{sandbox_id}'); report if "
            f"it persists."
        )

    # 6. Fallthrough — genuinely unexpected combination
    extras: list[str] = []
    if reason:
        extras.append(f"stop_reason: '{reason}'")
    if recovery:
        extras.append(f"recovery_status: '{recovery}'")
    extras_str = (", " + ", ".join(extras)) if extras else ""
    return (
        f"Sandbox '{sandbox_id}' reached unexpected status '{status}' "
        f"(expected '{expected}'{extras_str}).\n"
        f"Hint: call sdk.sandboxes.get('{sandbox_id}') to inspect."
    )
