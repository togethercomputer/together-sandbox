"""Lifecycle helper — turns a non-running / non-terminated sandbox state into a
single actionable error message.

Mirrors ``together-sandbox-typescript/src/lifecycle.ts``.
"""

from __future__ import annotations

from typing import Any, Literal

# status_reason → hint when expecting "running" but ended up terminal.
_STATUS_REASON_HINTS: dict[str, str] = {
    "internal_error": (
        "Sandbox failed to start due to an internal error. Common causes: "
        "image not found or snapshot corrupted. Try re-creating from a "
        "known-good snapshot; if it persists, report it."
    ),
    "out_of_capacity": (
        "Sandbox could not be scheduled — the cluster is out of capacity. "
        "Retry shortly, or try a different cluster."
    ),
    "oom_killed": (
        "Sandbox was killed for exceeding its memory limit. Increase "
        "memory_bytes when creating the sandbox."
    ),
    "crashed": (
        "The VM crashed. A terminated sandbox is terminal — create a new "
        "sandbox from a known-good snapshot."
    ),
    "evicted": (
        "Sandbox was evicted from its node. A terminated sandbox is terminal — "
        "create a new sandbox from a snapshot."
    ),
    "node_lost": (
        "Sandbox's node was lost. A terminated sandbox is terminal — create a "
        "new sandbox from a snapshot."
    ),
    "cluster_lost": (
        "Sandbox's cluster was lost. A terminated sandbox is terminal — create "
        "a new sandbox from a snapshot."
    ),
}


def _unwrap(value: Any) -> Any:
    """Normalise enum-like values to their underlying string."""
    if value is None:
        return None
    return getattr(value, "value", value)


def describe_lifecycle_failure(
    sandbox: Any,
    expected: Literal["running", "terminated"],
) -> str:
    """Return a human-readable explanation + hint for why ``sandbox`` did not
    reach ``expected``.

    Order of precedence:
      1. ``status == "unrecovered"``            — crash recovery failed.
      2. ``status == "recovering"``             — auto-recovery in progress.
      3. ``status`` in ``starting | terminating`` — wait endpoint returned early.
      4. ``status == "failed_to_start"``        — never started; use ``status_reason``.
      5. Wrong terminal (``terminated`` ↔ ``running``) — use ``status_reason``.
      6. Fallthrough.

    The ``sandbox`` argument is duck-typed: any object with the attributes
    ``id``, ``status``, ``status_reason`` will work. Enum-valued fields are
    unwrapped to their underlying ``.value``.
    """
    sandbox_id = getattr(sandbox, "id", None) or "<unknown>"
    status = _unwrap(getattr(sandbox, "status", None)) or "<unknown>"
    reason = _unwrap(getattr(sandbox, "status_reason", None))

    # 1. Unrecovered — crash recovery failed; terminal, biggest signal
    if status == "unrecovered":
        reason_bit = f", status_reason: '{reason}'" if reason else ""
        return (
            f"Sandbox '{sandbox_id}' could not be recovered "
            f"(status: 'unrecovered'{reason_bit}).\n"
            f"Hint: this sandbox cannot be recovered — create a new sandbox "
            f"from a snapshot."
        )

    # 2. Recovering — wait, do not retry blindly
    if status == "recovering":
        reason_bit = f", status_reason: '{reason}'" if reason else ""
        return (
            f"Sandbox '{sandbox_id}' is currently being auto-recovered "
            f"(status: 'recovering'{reason_bit}).\n"
            f"Hint: recovery is in progress — wait a few seconds then retry "
            f"sdk.sandboxes.get('{sandbox_id}'). If it becomes 'unrecovered' "
            f"you'll need to create a new sandbox."
        )

    # 3. Transient — wait returned without reaching a terminal status
    if status in ("starting", "terminating"):
        return (
            f"Sandbox '{sandbox_id}' is still in transient state '{status}' "
            f"after wait returned.\n"
            f"Hint: this is unexpected (wait_for_sandbox should only return "
            f"at a terminal status). Retry sdk.sandboxes.get('{sandbox_id}') "
            f"to check progress; report if it persists."
        )

    # 4. Failed to start — never reached running
    if expected == "running" and status == "failed_to_start":
        hint = _STATUS_REASON_HINTS.get(reason or "") or (
            "The sandbox never started — create a new sandbox from a "
            "known-good snapshot."
        )
        reason_bit = f" (status_reason: '{reason}')" if reason else ""
        return (
            f"Sandbox '{sandbox_id}' failed to start{reason_bit}.\n"
            f"Hint: {hint}"
        )

    # 5. Wrong terminal — reached the other end
    if expected == "running" and status == "terminated":
        hint = _STATUS_REASON_HINTS.get(reason or "") or (
            f"A terminated sandbox is terminal — create a new sandbox from a "
            f"snapshot, or call sdk.sandboxes.get('{sandbox_id}') to inspect."
        )
        reason_bit = f" (status_reason: '{reason}')" if reason else ""
        return (
            f"Sandbox '{sandbox_id}' terminated instead of reaching 'running'"
            f"{reason_bit}.\nHint: {hint}"
        )

    if expected == "terminated" and status == "running":
        return (
            f"Sandbox '{sandbox_id}' is still running — the terminate request "
            f"did not take effect.\n"
            f"Hint: retry sdk.sandboxes.terminate('{sandbox_id}'); report if "
            f"it persists."
        )

    # 6. Fallthrough — genuinely unexpected combination
    extras: list[str] = []
    if reason:
        extras.append(f"status_reason: '{reason}'")
    extras_str = (", " + ", ".join(extras)) if extras else ""
    return (
        f"Sandbox '{sandbox_id}' reached unexpected status '{status}' "
        f"(expected '{expected}'{extras_str}).\n"
        f"Hint: call sdk.sandboxes.get('{sandbox_id}') to inspect."
    )
