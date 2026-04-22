from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSandboxBody")


@_attrs_define
class CreateSandboxBody:
    """
    Attributes:
        millicpu (int): CPU allocation in millicpu. Must be > 0 and a multiple of 250.
        memory_bytes (int): Memory allocation in bytes. Must be > 0.
        disk_bytes (int): Disk allocation in bytes. Must be > 0.
        id (str | Unset): Sandbox ID (6–8 characters). Generated if not provided.
        snapshot_id (UUID | Unset): ID of the snapshot to use. One of snapshot_id or snapshot_alias is required.
        snapshot_alias (str | Unset): Alias of the snapshot to use. One of snapshot_id or snapshot_alias is required.
        ephemeral (bool | Unset):
    """

    millicpu: int
    memory_bytes: int
    disk_bytes: int
    id: str | Unset = UNSET
    snapshot_id: UUID | Unset = UNSET
    snapshot_alias: str | Unset = UNSET
    ephemeral: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        millicpu = self.millicpu

        memory_bytes = self.memory_bytes

        disk_bytes = self.disk_bytes

        id = self.id

        snapshot_id: str | Unset = UNSET
        if not isinstance(self.snapshot_id, Unset):
            snapshot_id = str(self.snapshot_id)

        snapshot_alias = self.snapshot_alias

        ephemeral = self.ephemeral

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "millicpu": millicpu,
                "memory_bytes": memory_bytes,
                "disk_bytes": disk_bytes,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if snapshot_id is not UNSET:
            field_dict["snapshot_id"] = snapshot_id
        if snapshot_alias is not UNSET:
            field_dict["snapshot_alias"] = snapshot_alias
        if ephemeral is not UNSET:
            field_dict["ephemeral"] = ephemeral

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        millicpu = d.pop("millicpu")

        memory_bytes = d.pop("memory_bytes")

        disk_bytes = d.pop("disk_bytes")

        id = d.pop("id", UNSET)

        _snapshot_id = d.pop("snapshot_id", UNSET)
        snapshot_id: UUID | Unset
        if isinstance(_snapshot_id, Unset):
            snapshot_id = UNSET
        else:
            snapshot_id = UUID(_snapshot_id)

        snapshot_alias = d.pop("snapshot_alias", UNSET)

        ephemeral = d.pop("ephemeral", UNSET)

        create_sandbox_body = cls(
            millicpu=millicpu,
            memory_bytes=memory_bytes,
            disk_bytes=disk_bytes,
            id=id,
            snapshot_id=snapshot_id,
            snapshot_alias=snapshot_alias,
            ephemeral=ephemeral,
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
