from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PreviewToken")


@_attrs_define
class PreviewToken:
    """
    Attributes:
        expires_at (None | str):
        last_used_at (None | str):
        token_id (str):
        token_prefix (str):
    """

    expires_at: None | str
    last_used_at: None | str
    token_id: str
    token_prefix: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expires_at: None | str
        expires_at = self.expires_at

        last_used_at: None | str
        last_used_at = self.last_used_at

        token_id = self.token_id

        token_prefix = self.token_prefix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "expires_at": expires_at,
                "last_used_at": last_used_at,
                "token_id": token_id,
                "token_prefix": token_prefix,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_expires_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        expires_at = _parse_expires_at(d.pop("expires_at"))

        def _parse_last_used_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at"))

        token_id = d.pop("token_id")

        token_prefix = d.pop("token_prefix")

        preview_token = cls(
            expires_at=expires_at,
            last_used_at=last_used_at,
            token_id=token_id,
            token_prefix=token_prefix,
        )

        preview_token.additional_properties = d
        return preview_token

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
