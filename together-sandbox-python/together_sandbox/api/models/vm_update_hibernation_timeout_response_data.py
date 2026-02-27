from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VMUpdateHibernationTimeoutResponseData")


@_attrs_define
class VMUpdateHibernationTimeoutResponseData:
    """
    Attributes:
        hibernation_timeout_seconds (int):
        id (str):
    """

    hibernation_timeout_seconds: int
    id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hibernation_timeout_seconds = self.hibernation_timeout_seconds

        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hibernation_timeout_seconds": hibernation_timeout_seconds,
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hibernation_timeout_seconds = d.pop("hibernation_timeout_seconds")

        id = d.pop("id")

        vm_update_hibernation_timeout_response_data = cls(
            hibernation_timeout_seconds=hibernation_timeout_seconds,
            id=id,
        )

        vm_update_hibernation_timeout_response_data.additional_properties = d
        return vm_update_hibernation_timeout_response_data

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
