from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VMUpdateHibernationTimeoutRequest")


@_attrs_define
class VMUpdateHibernationTimeoutRequest:
    """
    Attributes:
        hibernation_timeout_seconds (int): The new hibernation timeout in seconds.

            Must be greater than 0 and less than or equal to 86400 (24 hours).
             Example: 300.
    """

    hibernation_timeout_seconds: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hibernation_timeout_seconds = self.hibernation_timeout_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hibernation_timeout_seconds": hibernation_timeout_seconds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hibernation_timeout_seconds = d.pop("hibernation_timeout_seconds")

        vm_update_hibernation_timeout_request = cls(
            hibernation_timeout_seconds=hibernation_timeout_seconds,
        )

        vm_update_hibernation_timeout_request.additional_properties = d
        return vm_update_hibernation_timeout_request

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
