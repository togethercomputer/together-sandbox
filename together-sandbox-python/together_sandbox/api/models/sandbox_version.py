from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="SandboxVersion")


@_attrs_define
class SandboxVersion:
    """
    Attributes:
        id (UUID):
        sandbox_id (str): Short identifier (6–8 characters).
        number (int):
        snapshot_id (UUID):
        created_at (datetime.datetime):
    """

    id: UUID
    sandbox_id: str
    number: int
    snapshot_id: UUID
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        sandbox_id = self.sandbox_id

        number = self.number

        snapshot_id = str(self.snapshot_id)

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "sandbox_id": sandbox_id,
                "number": number,
                "snapshot_id": snapshot_id,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        sandbox_id = d.pop("sandbox_id")

        number = d.pop("number")

        snapshot_id = UUID(d.pop("snapshot_id"))

        created_at = isoparse(d.pop("created_at"))

        sandbox_version = cls(
            id=id,
            sandbox_id=sandbox_id,
            number=number,
            snapshot_id=snapshot_id,
            created_at=created_at,
        )

        sandbox_version.additional_properties = d
        return sandbox_version

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
