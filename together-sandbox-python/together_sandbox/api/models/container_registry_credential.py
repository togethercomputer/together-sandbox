from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ContainerRegistryCredential")


@_attrs_define
class ContainerRegistryCredential:
    """
    Attributes:
        username (str):
        password (str):
        registry_url (str): Registry URL including the namespace path (e.g. registry.example.com/nbswy3dp).
        expired_at (datetime.datetime | None):
    """

    username: str
    password: str
    registry_url: str
    expired_at: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        password = self.password

        registry_url = self.registry_url

        expired_at: None | str
        if isinstance(self.expired_at, datetime.datetime):
            expired_at = self.expired_at.isoformat()
        else:
            expired_at = self.expired_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "password": password,
                "registry_url": registry_url,
                "expired_at": expired_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username")

        password = d.pop("password")

        registry_url = d.pop("registry_url")

        def _parse_expired_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expired_at_type_0 = isoparse(data)

                return expired_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        expired_at = _parse_expired_at(d.pop("expired_at"))

        container_registry_credential = cls(
            username=username,
            password=password,
            registry_url=registry_url,
            expired_at=expired_at,
        )

        container_registry_credential.additional_properties = d
        return container_registry_credential

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
