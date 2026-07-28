from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tags import Tags
    from ..models.termination_policy import TerminationPolicy


T = TypeVar("T", bound="CreateSandboxBody")


@_attrs_define
class CreateSandboxBody:
    """
    Attributes:
        snapshot_id (UUID | Unset): ID of the snapshot to use. One of snapshot_id or snapshot_alias is required.
        snapshot_alias (str | Unset): Alias of the snapshot to use. One of snapshot_id or snapshot_alias is required.
        cpu (float | Unset): CPU allocation in cores. Defaults to 1 when omitted.
             Default: 1.0.
        memory_bytes (int | Unset): Memory allocation in bytes. Must be between 1 GB and 8 GB per requested CPU.
            Defaults to 2 GB when omitted.
             Default: 2000000000.
        ttl (int | Unset): Seconds after creation before the sandbox is automatically terminated. Must be > 0. Omit to
            disable automatic termination.
        tags (Tags | Unset): User-defined key-value labels (both keys and values are strings).
        termination_policy (TerminationPolicy | Unset): The policy applied when a sandbox terminates.
    """

    snapshot_id: UUID | Unset = UNSET
    snapshot_alias: str | Unset = UNSET
    cpu: float | Unset = 1.0
    memory_bytes: int | Unset = 2000000000
    ttl: int | Unset = UNSET
    tags: Tags | Unset = UNSET
    termination_policy: TerminationPolicy | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        snapshot_id: str | Unset = UNSET
        if not isinstance(self.snapshot_id, Unset):
            snapshot_id = str(self.snapshot_id)

        snapshot_alias = self.snapshot_alias

        cpu = self.cpu

        memory_bytes = self.memory_bytes

        ttl = self.ttl

        tags: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        termination_policy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.termination_policy, Unset):
            termination_policy = self.termination_policy.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if snapshot_id is not UNSET:
            field_dict["snapshot_id"] = snapshot_id
        if snapshot_alias is not UNSET:
            field_dict["snapshot_alias"] = snapshot_alias
        if cpu is not UNSET:
            field_dict["cpu"] = cpu
        if memory_bytes is not UNSET:
            field_dict["memory_bytes"] = memory_bytes
        if ttl is not UNSET:
            field_dict["ttl"] = ttl
        if tags is not UNSET:
            field_dict["tags"] = tags
        if termination_policy is not UNSET:
            field_dict["termination_policy"] = termination_policy

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.tags import Tags
        from ..models.termination_policy import TerminationPolicy

        d = dict(src_dict)
        _snapshot_id = d.pop("snapshot_id", UNSET)
        snapshot_id: UUID | Unset
        if isinstance(_snapshot_id, Unset):
            snapshot_id = UNSET
        else:
            snapshot_id = UUID(_snapshot_id)

        snapshot_alias = d.pop("snapshot_alias", UNSET)

        cpu = d.pop("cpu", UNSET)

        memory_bytes = d.pop("memory_bytes", UNSET)

        ttl = d.pop("ttl", UNSET)

        _tags = d.pop("tags", UNSET)
        tags: Tags | Unset
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = Tags.from_dict(_tags)

        _termination_policy = d.pop("termination_policy", UNSET)
        termination_policy: TerminationPolicy | Unset
        if isinstance(_termination_policy, Unset):
            termination_policy = UNSET
        else:
            termination_policy = TerminationPolicy.from_dict(_termination_policy)

        create_sandbox_body = cls(
            snapshot_id=snapshot_id,
            snapshot_alias=snapshot_alias,
            cpu=cpu,
            memory_bytes=memory_bytes,
            ttl=ttl,
            tags=tags,
            termination_policy=termination_policy,
        )

        create_sandbox_body.additional_properties = d
        return create_sandbox_body

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
