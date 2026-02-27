from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.preview_host_list_response_data_preview_hosts_item import PreviewHostListResponseDataPreviewHostsItem


T = TypeVar("T", bound="PreviewHostListResponseData")


@_attrs_define
class PreviewHostListResponseData:
    """
    Attributes:
        preview_hosts (list[PreviewHostListResponseDataPreviewHostsItem]):
    """

    preview_hosts: list[PreviewHostListResponseDataPreviewHostsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        preview_hosts = []
        for preview_hosts_item_data in self.preview_hosts:
            preview_hosts_item = preview_hosts_item_data.to_dict()
            preview_hosts.append(preview_hosts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "preview_hosts": preview_hosts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preview_host_list_response_data_preview_hosts_item import (
            PreviewHostListResponseDataPreviewHostsItem,
        )

        d = dict(src_dict)
        preview_hosts = []
        _preview_hosts = d.pop("preview_hosts")
        for preview_hosts_item_data in _preview_hosts:
            preview_hosts_item = PreviewHostListResponseDataPreviewHostsItem.from_dict(preview_hosts_item_data)

            preview_hosts.append(preview_hosts_item)

        preview_host_list_response_data = cls(
            preview_hosts=preview_hosts,
        )

        preview_host_list_response_data.additional_properties = d
        return preview_host_list_response_data

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
