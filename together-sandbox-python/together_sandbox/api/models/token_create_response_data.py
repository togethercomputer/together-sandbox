from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TokenCreateResponseData")


@_attrs_define
class TokenCreateResponseData:
    """
    Attributes:
        description (None | str):
        expires_at (None | str):
        scopes (list[str]):
        team_id (str):
        token (str):
        token_id (str):
    """

    description: None | str
    expires_at: None | str
    scopes: list[str]
    team_id: str
    token: str
    token_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description: None | str
        description = self.description

        expires_at: None | str
        expires_at = self.expires_at

        scopes = self.scopes

        team_id = self.team_id

        token = self.token

        token_id = self.token_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "expires_at": expires_at,
                "scopes": scopes,
                "team_id": team_id,
                "token": token,
                "token_id": token_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        def _parse_expires_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        expires_at = _parse_expires_at(d.pop("expires_at"))

        scopes = cast(list[str], d.pop("scopes"))

        team_id = d.pop("team_id")

        token = d.pop("token")

        token_id = d.pop("token_id")

        token_create_response_data = cls(
            description=description,
            expires_at=expires_at,
            scopes=scopes,
            team_id=team_id,
            token=token,
            token_id=token_id,
        )

        token_create_response_data.additional_properties = d
        return token_create_response_data

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
