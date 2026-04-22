from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.snapshot_alias_type import SnapshotAliasType

T = TypeVar("T", bound="SnapshotAlias")


@_attrs_define
class SnapshotAlias:
    """
    Attributes:
        field_type_ (SnapshotAliasType):
        id (UUID):
        snapshot_id (UUID):
        alias (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    field_type_: SnapshotAliasType
    id: UUID
    snapshot_id: UUID
    alias: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_type_ = self.field_type_.value

        id = str(self.id)

        snapshot_id = str(self.snapshot_id)

        alias = self.alias

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_type": field_type_,
                "id": id,
                "snapshot_id": snapshot_id,
                "alias": alias,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field_type_ = SnapshotAliasType(d.pop("_type"))

        id = UUID(d.pop("id"))

        snapshot_id = UUID(d.pop("snapshot_id"))

        alias = d.pop("alias")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        snapshot_alias = cls(
            field_type_=field_type_,
            id=id,
            snapshot_id=snapshot_id,
            alias=alias,
            created_at=created_at,
            updated_at=updated_at,
        )

        snapshot_alias.additional_properties = d
        return snapshot_alias

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
