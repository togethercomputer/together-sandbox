from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.sandbox_status import SandboxStatus
from ..models.sandbox_status_reason import SandboxStatusReason

if TYPE_CHECKING:
    from ..models.sandbox_agent import SandboxAgent
    from ..models.tags import Tags
    from ..models.termination_policy import TerminationPolicy


T = TypeVar("T", bound="Sandbox")


@_attrs_define
class Sandbox:
    """
    Attributes:
        id (UUID): The sandbox's unique identifier.
        organization_id (None | str):
        project_id (str):
        status (SandboxStatus):
        snapshot_id (UUID): The snapshot the sandbox boots from. The snapshot produced when the sandbox terminates is
            aliased as `sandbox:<sandbox id>`.
        cpu (float): CPU allocation in cores.
        memory_bytes (int): Memory allocation in bytes.
        agent (SandboxAgent): Connection details for the in-sandbox agent.
        ttl (int | None): Seconds after creation before the sandbox is automatically terminated. Null disables automatic
            termination.
        tags (Tags): User-defined key-value labels (both keys and values are strings).
        termination_policy (None | TerminationPolicy): The termination policy, or null for an ephemeral sandbox (no
            snapshot is taken and it is deleted on termination).
        created_at (datetime.datetime):
        started_at (datetime.datetime | None):
        terminated_at (datetime.datetime | None):
        status_reason (SandboxStatusReason):
        resized_at (datetime.datetime | None):
        recovery_at (datetime.datetime | None):
        updated_at (datetime.datetime):
    """

    id: UUID
    organization_id: None | str
    project_id: str
    status: SandboxStatus
    snapshot_id: UUID
    cpu: float
    memory_bytes: int
    agent: SandboxAgent
    ttl: int | None
    tags: Tags
    termination_policy: None | TerminationPolicy
    created_at: datetime.datetime
    started_at: datetime.datetime | None
    terminated_at: datetime.datetime | None
    status_reason: SandboxStatusReason
    resized_at: datetime.datetime | None
    recovery_at: datetime.datetime | None
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.termination_policy import TerminationPolicy

        id = str(self.id)

        organization_id: None | str
        organization_id = self.organization_id

        project_id = self.project_id

        status = self.status.value

        snapshot_id = str(self.snapshot_id)

        cpu = self.cpu

        memory_bytes = self.memory_bytes

        agent = self.agent.to_dict()

        ttl: int | None
        ttl = self.ttl

        tags = self.tags.to_dict()

        termination_policy: dict[str, Any] | None
        if isinstance(self.termination_policy, TerminationPolicy):
            termination_policy = self.termination_policy.to_dict()
        else:
            termination_policy = self.termination_policy

        created_at = self.created_at.isoformat()

        started_at: None | str
        if isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        terminated_at: None | str
        if isinstance(self.terminated_at, datetime.datetime):
            terminated_at = self.terminated_at.isoformat()
        else:
            terminated_at = self.terminated_at

        status_reason = self.status_reason.value

        resized_at: None | str
        if isinstance(self.resized_at, datetime.datetime):
            resized_at = self.resized_at.isoformat()
        else:
            resized_at = self.resized_at

        recovery_at: None | str
        if isinstance(self.recovery_at, datetime.datetime):
            recovery_at = self.recovery_at.isoformat()
        else:
            recovery_at = self.recovery_at

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "organization_id": organization_id,
                "project_id": project_id,
                "status": status,
                "snapshot_id": snapshot_id,
                "cpu": cpu,
                "memory_bytes": memory_bytes,
                "agent": agent,
                "ttl": ttl,
                "tags": tags,
                "termination_policy": termination_policy,
                "created_at": created_at,
                "started_at": started_at,
                "terminated_at": terminated_at,
                "status_reason": status_reason,
                "resized_at": resized_at,
                "recovery_at": recovery_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.sandbox_agent import SandboxAgent
        from ..models.tags import Tags
        from ..models.termination_policy import TerminationPolicy

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        def _parse_organization_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        organization_id = _parse_organization_id(d.pop("organization_id"))

        project_id = d.pop("project_id")

        status = SandboxStatus(d.pop("status"))

        snapshot_id = UUID(d.pop("snapshot_id"))

        cpu = d.pop("cpu")

        memory_bytes = d.pop("memory_bytes")

        agent = SandboxAgent.from_dict(d.pop("agent"))

        def _parse_ttl(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        ttl = _parse_ttl(d.pop("ttl"))

        tags = Tags.from_dict(d.pop("tags"))

        def _parse_termination_policy(data: object) -> None | TerminationPolicy:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                termination_policy_type_0 = TerminationPolicy.from_dict(data)

                return termination_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TerminationPolicy, data)

        termination_policy = _parse_termination_policy(d.pop("termination_policy"))

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        def _parse_started_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = datetime.datetime.fromisoformat(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        started_at = _parse_started_at(d.pop("started_at"))

        def _parse_terminated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                terminated_at_type_0 = datetime.datetime.fromisoformat(data)

                return terminated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        terminated_at = _parse_terminated_at(d.pop("terminated_at"))

        status_reason = SandboxStatusReason(d.pop("status_reason"))

        def _parse_resized_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                resized_at_type_0 = datetime.datetime.fromisoformat(data)

                return resized_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        resized_at = _parse_resized_at(d.pop("resized_at"))

        def _parse_recovery_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recovery_at_type_0 = datetime.datetime.fromisoformat(data)

                return recovery_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        recovery_at = _parse_recovery_at(d.pop("recovery_at"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        sandbox = cls(
            id=id,
            organization_id=organization_id,
            project_id=project_id,
            status=status,
            snapshot_id=snapshot_id,
            cpu=cpu,
            memory_bytes=memory_bytes,
            agent=agent,
            ttl=ttl,
            tags=tags,
            termination_policy=termination_policy,
            created_at=created_at,
            started_at=started_at,
            terminated_at=terminated_at,
            status_reason=status_reason,
            resized_at=resized_at,
            recovery_at=recovery_at,
            updated_at=updated_at,
        )

        sandbox.additional_properties = d
        return sandbox

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
