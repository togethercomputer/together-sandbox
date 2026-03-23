from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vm_list_clusters_response_data_clusters_item import (
        VMListClustersResponseDataClustersItem,
    )


T = TypeVar("T", bound="VMListClustersResponseData")


@_attrs_define
class VMListClustersResponseData:
    """
    Attributes:
        clusters (list[VMListClustersResponseDataClustersItem]):
    """

    clusters: list[VMListClustersResponseDataClustersItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        clusters = []
        for clusters_item_data in self.clusters:
            clusters_item = clusters_item_data.to_dict()
            clusters.append(clusters_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "clusters": clusters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vm_list_clusters_response_data_clusters_item import (
            VMListClustersResponseDataClustersItem,
        )

        d = dict(src_dict)
        clusters = []
        _clusters = d.pop("clusters")
        for clusters_item_data in _clusters:
            clusters_item = VMListClustersResponseDataClustersItem.from_dict(
                clusters_item_data
            )

            clusters.append(clusters_item)

        vm_list_clusters_response_data = cls(
            clusters=clusters,
        )

        vm_list_clusters_response_data.additional_properties = d
        return vm_list_clusters_response_data

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
