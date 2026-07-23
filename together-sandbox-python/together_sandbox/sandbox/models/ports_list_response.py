from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.port_info import PortInfo


T = TypeVar("T", bound="PortsListResponse")


@_attrs_define
class PortsListResponse:
    """
    Attributes:
        ports (list[PortInfo]): List of open ports
    """

    ports: list[PortInfo]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ports = []
        for ports_item_data in self.ports:
            ports_item = ports_item_data.to_dict()
            ports.append(ports_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ports": ports,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.port_info import PortInfo

        d = dict(src_dict)
        ports = []
        _ports = d.pop("ports")
        for ports_item_data in _ports:
            ports_item = PortInfo.from_dict(ports_item_data)

            ports.append(ports_item)

        ports_list_response = cls(
            ports=ports,
        )

        ports_list_response.additional_properties = d
        return ports_list_response

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
