from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sandbox_settings import SandboxSettings


T = TypeVar("T", bound="Sandbox")


@_attrs_define
class Sandbox:
    """
    Attributes:
        created_at (datetime.datetime):
        id (str):
        is_frozen (bool):
        privacy (int):
        settings (SandboxSettings):
        tags (list[str]):
        updated_at (datetime.datetime):
        description (None | str | Unset):
        title (None | str | Unset):
    """

    created_at: datetime.datetime
    id: str
    is_frozen: bool
    privacy: int
    settings: SandboxSettings
    tags: list[str]
    updated_at: datetime.datetime
    description: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = self.id

        is_frozen = self.is_frozen

        privacy = self.privacy

        settings = self.settings.to_dict()

        tags = self.tags

        updated_at = self.updated_at.isoformat()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "id": id,
                "is_frozen": is_frozen,
                "privacy": privacy,
                "settings": settings,
                "tags": tags,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sandbox_settings import SandboxSettings

        d = dict(src_dict)
        created_at = isoparse(d.pop("created_at"))

        id = d.pop("id")

        is_frozen = d.pop("is_frozen")

        privacy = d.pop("privacy")

        settings = SandboxSettings.from_dict(d.pop("settings"))

        tags = cast(list[str], d.pop("tags"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        sandbox = cls(
            created_at=created_at,
            id=id,
            is_frozen=is_frozen,
            privacy=privacy,
            settings=settings,
            tags=tags,
            updated_at=updated_at,
            description=description,
            title=title,
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
