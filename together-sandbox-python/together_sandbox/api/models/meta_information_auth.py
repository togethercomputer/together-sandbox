from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MetaInformationAuth")


@_attrs_define
class MetaInformationAuth:
    """Meta information about the current authentication context

    Attributes:
        scopes (list[str]):
        team (None | UUID):
        version (str):
    """

    scopes: list[str]
    team: None | UUID
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scopes = self.scopes

        team: None | str
        if isinstance(self.team, UUID):
            team = str(self.team)
        else:
            team = self.team

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scopes": scopes,
                "team": team,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        scopes = cast(list[str], d.pop("scopes"))

        def _parse_team(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                team_type_0 = UUID(data)

                return team_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        team = _parse_team(d.pop("team"))

        version = d.pop("version")

        meta_information_auth = cls(
            scopes=scopes,
            team=team,
            version=version,
        )

        meta_information_auth.additional_properties = d
        return meta_information_auth

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
