from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VMAssignTagAliasResponseData")


@_attrs_define
class VMAssignTagAliasResponseData:
    """
    Attributes:
        alias (str):
        namespace (str):
        tag_alias_id (str):
        tag_id (str):
        team_id (str):
    """

    alias: str
    namespace: str
    tag_alias_id: str
    tag_id: str
    team_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        alias = self.alias

        namespace = self.namespace

        tag_alias_id = self.tag_alias_id

        tag_id = self.tag_id

        team_id = self.team_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "alias": alias,
                "namespace": namespace,
                "tag_alias_id": tag_alias_id,
                "tag_id": tag_id,
                "team_id": team_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        alias = d.pop("alias")

        namespace = d.pop("namespace")

        tag_alias_id = d.pop("tag_alias_id")

        tag_id = d.pop("tag_id")

        team_id = d.pop("team_id")

        vm_assign_tag_alias_response_data = cls(
            alias=alias,
            namespace=namespace,
            tag_alias_id=tag_alias_id,
            tag_id=tag_id,
            team_id=team_id,
        )

        vm_assign_tag_alias_response_data.additional_properties = d
        return vm_assign_tag_alias_response_data

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
