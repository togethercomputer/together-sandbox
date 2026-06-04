"""Public, hand-written facade types for the Together Sandbox SDK.

These dataclasses and ``Literal`` unions are the SDK's public contract. They
mirror the wire shapes of the generated OpenAPI clients but are owned by this
module, so the generated attrs models (with their ``UNSET`` sentinels,
``to_dict``/``from_dict`` and ``additional_properties`` machinery) never appear
in the public API. See ``EXPORTED_TYPES.md`` at the repo root for the policy.

Conversion from the generated models/SSE payloads happens at the facade
boundary via the ``_*_from_model`` / ``_*_from_dict`` adapters below.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypedDict

# Internal generated types — imported only to convert away from them.
from ._api.models.sandbox import Sandbox as _SandboxModel
from ._api.models.snapshot import Snapshot as _SnapshotModel
from ._sandbox_client.models.file_info import FileInfo as _FileInfoModel
from ._sandbox_client.models.exec_item import ExecItem as _ExecItemModel
from ._sandbox_client.models.port_info import PortInfo as _PortInfoModel
from ._sandbox_client.types import UNSET

# ─── Sandbox lifecycle ────────────────────────────────────────────────────────

SandboxStatus = Literal["created", "starting", "running", "stopping", "stopped"]
StartType = Literal["resume", "cold_start"]
StopReason = Literal[
    "start_failed",
    "shutdown",
    "hibernated",
    "crashed",
    "oom_killed",
    "evicted",
    "node_lost",
    "cluster_lost",
]
RecoveryStatus = Literal["pending", "recovered", "canceled", "unrecoverable"]


@dataclass(frozen=True)
class SandboxInfo:
    """Information about a sandbox VM (returned by ``sdk.sandboxes.create()``
    and exposed as ``sandbox.vm_info``)."""

    id: str
    project_id: str
    status: SandboxStatus
    ephemeral: bool
    cluster_name: str
    current_version_number: int
    next_version_number: int
    millicpu: int
    gpu: int
    memory_bytes: int
    disk_bytes: int
    version_count: int
    agent_version: str
    agent_type: str
    agent_token: str
    agent_url: str
    created_at: datetime
    start_requested_at: datetime | None
    start_type: StartType | None
    started_at: datetime | None
    stop_requested_at: datetime | None
    requested_stop_type: Literal["shutdown", "hibernate"] | None
    stopped_at: datetime | None
    stop_reason: StopReason | None
    specs_updated_at: datetime | None
    recovery_status: RecoveryStatus | None
    recovery_started_at: datetime | None
    recovery_finished_at: datetime | None
    updated_at: datetime


# ─── Snapshots ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Snapshot:
    """A registered snapshot (returned by ``snapshots.get_by_id/get_by_alias/list``)."""

    id: str
    project_id: str
    byte_size: int
    protected: bool
    optimized: bool
    includes_memory_snapshot: bool
    created_at: datetime
    optimized_at: datetime | None
    updated_at: datetime


# ─── File system ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FileInfo:
    """Metadata for a file or directory (returned by ``files.stat()`` and
    ``directories.list()``)."""

    name: str
    path: str
    is_dir: bool
    size: int
    mod_time: str


WatcherEventType = Literal["ADD", "REMOVE", "CHANGE", "connected", "error"]


@dataclass(frozen=True)
class WatcherEvent:
    """A file system change event emitted by ``files.watch()``."""

    paths: list[str]
    type: WatcherEventType
    timestamp: str


# ─── Execs ────────────────────────────────────────────────────────────────────

ExecStatus = str
ExecStreamKind = Literal["stdout", "stderr"]


@dataclass(frozen=True)
class ExecInfo:
    """Information about an exec (returned by ``execs.create/get/start/list/
    send_stdin``)."""

    id: str
    command: str
    args: list[str]
    status: ExecStatus
    pid: int
    pty: bool
    exit_code: int
    user: str | None = None


@dataclass(frozen=True)
class ExecOutputEvent:
    """A single exec output event emitted by ``execs.stream_output()``."""

    type: ExecStreamKind
    output: str
    sequence: int
    timestamp: str | None = None
    exit_code: int | None = None


class ExecResult(TypedDict):
    """Result of running a command to completion via ``execs.exec()``."""

    exit_code: int
    output: str


# ─── Ports ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PortInfo:
    """An open port discovered inside the sandbox (returned by ``ports.list()``)."""

    port: int
    address: str


# ─── Boundary adapters (generated model / SSE dict → facade) ───────────────────


def _enum_value(value: Any) -> Any:
    """Return the wire value of a generated enum, passing through ``None``/plain
    strings unchanged."""
    if value is None:
        return None
    return getattr(value, "value", value)


def _sandbox_info_from_model(m: _SandboxModel) -> SandboxInfo:
    return SandboxInfo(
        id=m.id,
        project_id=m.project_id,
        status=_enum_value(m.status),
        ephemeral=m.ephemeral,
        cluster_name=m.cluster_name,
        current_version_number=m.current_version_number,
        next_version_number=m.next_version_number,
        millicpu=m.millicpu,
        gpu=m.gpu,
        memory_bytes=m.memory_bytes,
        disk_bytes=m.disk_bytes,
        version_count=m.version_count,
        agent_version=m.agent_version,
        agent_type=m.agent_type,
        agent_token=m.agent_token,
        agent_url=m.agent_url,
        created_at=m.created_at,
        start_requested_at=m.start_requested_at,
        start_type=_enum_value(m.start_type),
        started_at=m.started_at,
        stop_requested_at=m.stop_requested_at,
        requested_stop_type=_enum_value(m.requested_stop_type),
        stopped_at=m.stopped_at,
        stop_reason=_enum_value(m.stop_reason),
        specs_updated_at=m.specs_updated_at,
        recovery_status=_enum_value(m.recovery_status),
        recovery_started_at=m.recovery_started_at,
        recovery_finished_at=m.recovery_finished_at,
        updated_at=m.updated_at,
    )


def _snapshot_from_model(m: _SnapshotModel) -> Snapshot:
    return Snapshot(
        id=str(m.id),
        project_id=m.project_id,
        byte_size=m.byte_size,
        protected=m.protected,
        optimized=m.optimized,
        includes_memory_snapshot=m.includes_memory_snapshot,
        created_at=m.created_at,
        optimized_at=m.optimized_at,
        updated_at=m.updated_at,
    )


def _file_info_from_model(m: _FileInfoModel) -> FileInfo:
    return FileInfo(
        name=m.name,
        path=m.path,
        is_dir=m.is_dir,
        size=m.size,
        mod_time=m.mod_time,
    )


def _exec_info_from_model(m: _ExecItemModel) -> ExecInfo:
    return ExecInfo(
        id=m.id,
        command=m.command,
        args=list(m.args),
        status=m.status,
        pid=m.pid,
        pty=m.pty,
        exit_code=m.exit_code,
        user=None if m.user is UNSET else m.user,
    )


def _port_info_from_model(m: _PortInfoModel) -> PortInfo:
    return PortInfo(port=m.port, address=m.address)


def _exec_info_from_dict(d: dict[str, Any]) -> ExecInfo:
    return ExecInfo(
        id=d["id"],
        command=d.get("command", ""),
        args=list(d.get("args", [])),
        status=d.get("status", ""),
        pid=d.get("pid", 0),
        pty=d.get("pty", False),
        exit_code=d.get("exitCode", 0),
        user=d.get("user"),
    )


def _exec_output_event_from_dict(d: dict[str, Any]) -> ExecOutputEvent:
    return ExecOutputEvent(
        type=d.get("type", "stdout"),
        output=d.get("output", ""),
        sequence=d.get("sequence", 0),
        timestamp=d.get("timestamp"),
        exit_code=d.get("exitCode"),
    )


def _watcher_event_from_dict(d: dict[str, Any]) -> WatcherEvent:
    return WatcherEvent(
        paths=list(d.get("paths", [])),
        type=d.get("type", "error"),
        timestamp=d.get("timestamp", ""),
    )


def _port_info_from_dict(d: dict[str, Any]) -> PortInfo:
    return PortInfo(port=d["port"], address=d["address"])
