from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.snapshot_tags import SnapshotTags


T = TypeVar("T", bound="Snapshot")


@_attrs_define
class Snapshot:
    """
    Attributes:
        id (UUID):
        organization_id (None | str):
        project_id (str):
        byte_size (int):
        tags (SnapshotTags): Arbitrary key/value labels attached to the snapshot.
        ttl (int | None): Seconds after creation before the snapshot is automatically retired. Null disables automatic
            retirement.
        memory (bool): Whether the snapshot includes a memory snapshot in addition to the filesystem.
        created_at (datetime.datetime):
        retired_at (datetime.datetime | None): When the snapshot was retired, or null if it is still active. A retired
            snapshot is deleted after a short retention window.
        updated_at (datetime.datetime):
    """

    id: UUID
    organization_id: None | str
    project_id: str
    byte_size: int
    tags: SnapshotTags
    ttl: int | None
    memory: bool
    created_at: datetime.datetime
    retired_at: datetime.datetime | None
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        organization_id: None | str
        organization_id = self.organization_id

        project_id = self.project_id

        byte_size = self.byte_size

        tags = self.tags.to_dict()

        ttl: int | None
        ttl = self.ttl

        memory = self.memory

        created_at = self.created_at.isoformat()

        retired_at: None | str
        if isinstance(self.retired_at, datetime.datetime):
            retired_at = self.retired_at.isoformat()
        else:
            retired_at = self.retired_at

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "organization_id": organization_id,
                "project_id": project_id,
                "byte_size": byte_size,
                "tags": tags,
                "ttl": ttl,
                "memory": memory,
                "created_at": created_at,
                "retired_at": retired_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.snapshot_tags import SnapshotTags

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        def _parse_organization_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        organization_id = _parse_organization_id(d.pop("organization_id"))

        project_id = d.pop("project_id")

        byte_size = d.pop("byte_size")

        tags = SnapshotTags.from_dict(d.pop("tags"))

        def _parse_ttl(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        ttl = _parse_ttl(d.pop("ttl"))

        memory = d.pop("memory")

        created_at = isoparse(d.pop("created_at"))

        def _parse_retired_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                retired_at_type_0 = isoparse(data)

                return retired_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        retired_at = _parse_retired_at(d.pop("retired_at"))

        updated_at = isoparse(d.pop("updated_at"))

        snapshot = cls(
            id=id,
            organization_id=organization_id,
            project_id=project_id,
            byte_size=byte_size,
            tags=tags,
            ttl=ttl,
            memory=memory,
            created_at=created_at,
            retired_at=retired_at,
            updated_at=updated_at,
        )

        snapshot.additional_properties = d
        return snapshot

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
