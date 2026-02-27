from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PreviewHostListResponseDataPreviewHostsItem")


@_attrs_define
class PreviewHostListResponseDataPreviewHostsItem:
    """
    Attributes:
        host (str):
        inserted_at (str):
    """

    host: str
    inserted_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        host = self.host

        inserted_at = self.inserted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "host": host,
                "inserted_at": inserted_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host = d.pop("host")

        inserted_at = d.pop("inserted_at")

        preview_host_list_response_data_preview_hosts_item = cls(
            host=host,
            inserted_at=inserted_at,
        )

        preview_host_list_response_data_preview_hosts_item.additional_properties = d
        return preview_host_list_response_data_preview_hosts_item

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
