from __future__ import annotations
from dataclasses import dataclass


@dataclass
class StartOptions:
    """Options for starting a sandbox VM."""
    version_number: int | None = None


@dataclass
class CreateSandboxParams:
    """Parameters for creating a new sandbox."""
    millicpu: int
    memory_bytes: int
    disk_bytes: int
    id: str | None = None
    snapshot_id: str | None = None
    snapshot_alias: str | None = None
    ephemeral: bool | None = None