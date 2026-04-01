from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.token_create_request_scopes_item import TokenCreateRequestScopesItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenCreateRequest")


@_attrs_define
class TokenCreateRequest:
    """
    Attributes:
        default_version (datetime.date | None | Unset): API Version to use, formatted as YYYY-MM-DD. Defaults to the
            latest version at time of creation.
        description (str | Unset): Description of this token, for instance where it will be used.
        expires_at (datetime.datetime | None | Unset): UTC Timestamp until when this token is valid. Omitting this field
            will create a token without an expiry.
        scopes (list[TokenCreateRequestScopesItem] | Unset): Which scopes to grant this token. The given scopes will
            replace the current scopes, revoking any that are no longer present in the list.
    """

    default_version: datetime.date | None | Unset = UNSET
    description: str | Unset = UNSET
    expires_at: datetime.datetime | None | Unset = UNSET
    scopes: list[TokenCreateRequestScopesItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        default_version: None | str | Unset
        if isinstance(self.default_version, Unset):
            default_version = UNSET
        elif isinstance(self.default_version, datetime.date):
            default_version = self.default_version.isoformat()
        else:
            default_version = self.default_version

        description = self.description

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        scopes: list[str] | Unset = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = []
            for scopes_item_data in self.scopes:
                scopes_item = scopes_item_data.value
                scopes.append(scopes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_version is not UNSET:
            field_dict["default_version"] = default_version
        if description is not UNSET:
            field_dict["description"] = description
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if scopes is not UNSET:
            field_dict["scopes"] = scopes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_default_version(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                default_version_type_0 = isoparse(data).date()

                return default_version_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        default_version = _parse_default_version(d.pop("default_version", UNSET))

        description = d.pop("description", UNSET)

        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        _scopes = d.pop("scopes", UNSET)
        scopes: list[TokenCreateRequestScopesItem] | Unset = UNSET
        if _scopes is not UNSET:
            scopes = []
            for scopes_item_data in _scopes:
                scopes_item = TokenCreateRequestScopesItem(scopes_item_data)

                scopes.append(scopes_item)

        token_create_request = cls(
            default_version=default_version,
            description=description,
            expires_at=expires_at,
            scopes=scopes,
        )

        token_create_request.additional_properties = d
        return token_create_request

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
