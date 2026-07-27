from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_sandbox_body_tags import CreateSandboxBodyTags
    from ..models.termination_policy import TerminationPolicy


T = TypeVar("T", bound="CreateSandboxBody")


@_attrs_define
class CreateSandboxBody:
    """
    Attributes:
        cpu (float): CPU allocation in cores. Must be > 0 and a multiple of 0.25.
        memory_bytes (int): Memory allocation in bytes. Must be > 0.
        snapshot_id (UUID | Unset): ID of the snapshot to use. One of snapshot_id or snapshot_alias is required.
        snapshot_alias (str | Unset): Alias of the snapshot to use. One of snapshot_id or snapshot_alias is required.
        tags (CreateSandboxBodyTags | Unset): Arbitrary key/value labels to attach to the sandbox.
        ttl (int | Unset): Seconds after creation before the sandbox is automatically terminated. Must be > 0. Omit to
            disable automatic termination.
        termination_policy (TerminationPolicy | Unset): The snapshot policy applied when a sandbox terminates.
        cluster_name (str | Unset): Name of the cluster to launch the sandbox in.
    """

    cpu: float
    memory_bytes: int
    snapshot_id: UUID | Unset = UNSET
    snapshot_alias: str | Unset = UNSET
    tags: CreateSandboxBodyTags | Unset = UNSET
    ttl: int | Unset = UNSET
    termination_policy: TerminationPolicy | Unset = UNSET
    cluster_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cpu = self.cpu

        memory_bytes = self.memory_bytes

        snapshot_id: str | Unset = UNSET
        if not isinstance(self.snapshot_id, Unset):
            snapshot_id = str(self.snapshot_id)

        snapshot_alias = self.snapshot_alias

        tags: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        ttl = self.ttl

        termination_policy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.termination_policy, Unset):
            termination_policy = self.termination_policy.to_dict()

        cluster_name = self.cluster_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cpu": cpu,
                "memory_bytes": memory_bytes,
            }
        )
        if snapshot_id is not UNSET:
            field_dict["snapshot_id"] = snapshot_id
        if snapshot_alias is not UNSET:
            field_dict["snapshot_alias"] = snapshot_alias
        if tags is not UNSET:
            field_dict["tags"] = tags
        if ttl is not UNSET:
            field_dict["ttl"] = ttl
        if termination_policy is not UNSET:
            field_dict["termination_policy"] = termination_policy
        if cluster_name is not UNSET:
            field_dict["cluster_name"] = cluster_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_sandbox_body_tags import CreateSandboxBodyTags
        from ..models.termination_policy import TerminationPolicy

        d = dict(src_dict)
        cpu = d.pop("cpu")

        memory_bytes = d.pop("memory_bytes")

        _snapshot_id = d.pop("snapshot_id", UNSET)
        snapshot_id: UUID | Unset
        if isinstance(_snapshot_id, Unset):
            snapshot_id = UNSET
        else:
            snapshot_id = UUID(_snapshot_id)

        snapshot_alias = d.pop("snapshot_alias", UNSET)

        _tags = d.pop("tags", UNSET)
        tags: CreateSandboxBodyTags | Unset
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = CreateSandboxBodyTags.from_dict(_tags)

        ttl = d.pop("ttl", UNSET)

        _termination_policy = d.pop("termination_policy", UNSET)
        termination_policy: TerminationPolicy | Unset
        if isinstance(_termination_policy, Unset):
            termination_policy = UNSET
        else:
            termination_policy = TerminationPolicy.from_dict(_termination_policy)

        cluster_name = d.pop("cluster_name", UNSET)

        create_sandbox_body = cls(
            cpu=cpu,
            memory_bytes=memory_bytes,
            snapshot_id=snapshot_id,
            snapshot_alias=snapshot_alias,
            tags=tags,
            ttl=ttl,
            termination_policy=termination_policy,
            cluster_name=cluster_name,
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
