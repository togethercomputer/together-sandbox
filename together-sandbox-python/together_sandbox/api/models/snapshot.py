from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="Snapshot")


@_attrs_define
class Snapshot:
    """
    Attributes:
        id (UUID):
        project_id (str):
        byte_size (int):
        protected (bool):
        optimized (bool):
        includes_memory_snapshot (bool):
        created_at (datetime.datetime):
        optimized_at (datetime.datetime | None):
        updated_at (datetime.datetime):
    """

    id: UUID
    project_id: str
    byte_size: int
    protected: bool
    optimized: bool
    includes_memory_snapshot: bool
    created_at: datetime.datetime
    optimized_at: datetime.datetime | None
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        project_id = self.project_id

        byte_size = self.byte_size

        protected = self.protected

        optimized = self.optimized

        includes_memory_snapshot = self.includes_memory_snapshot

        created_at = self.created_at.isoformat()

        optimized_at: None | str
        if isinstance(self.optimized_at, datetime.datetime):
            optimized_at = self.optimized_at.isoformat()
        else:
            optimized_at = self.optimized_at

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "project_id": project_id,
                "byte_size": byte_size,
                "protected": protected,
                "optimized": optimized,
                "includes_memory_snapshot": includes_memory_snapshot,
                "created_at": created_at,
                "optimized_at": optimized_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        project_id = d.pop("project_id")

        byte_size = d.pop("byte_size")

        protected = d.pop("protected")

        optimized = d.pop("optimized")

        includes_memory_snapshot = d.pop("includes_memory_snapshot")

        created_at = isoparse(d.pop("created_at"))

        def _parse_optimized_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                optimized_at_type_0 = isoparse(data)

                return optimized_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        optimized_at = _parse_optimized_at(d.pop("optimized_at"))

        updated_at = isoparse(d.pop("updated_at"))

        snapshot = cls(
            id=id,
            project_id=project_id,
            byte_size=byte_size,
            protected=protected,
            optimized=optimized,
            includes_memory_snapshot=includes_memory_snapshot,
            created_at=created_at,
            optimized_at=optimized_at,
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
