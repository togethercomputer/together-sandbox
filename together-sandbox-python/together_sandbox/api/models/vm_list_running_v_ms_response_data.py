from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vm_list_running_v_ms_response_data_vms_item import VMListRunningVMsResponseDataVmsItem


T = TypeVar("T", bound="VMListRunningVMsResponseData")


@_attrs_define
class VMListRunningVMsResponseData:
    """
    Attributes:
        concurrent_vm_count (int):
        concurrent_vm_limit (int):
        vms (list[VMListRunningVMsResponseDataVmsItem]):
    """

    concurrent_vm_count: int
    concurrent_vm_limit: int
    vms: list[VMListRunningVMsResponseDataVmsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        concurrent_vm_count = self.concurrent_vm_count

        concurrent_vm_limit = self.concurrent_vm_limit

        vms = []
        for vms_item_data in self.vms:
            vms_item = vms_item_data.to_dict()
            vms.append(vms_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "concurrent_vm_count": concurrent_vm_count,
                "concurrent_vm_limit": concurrent_vm_limit,
                "vms": vms,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vm_list_running_v_ms_response_data_vms_item import VMListRunningVMsResponseDataVmsItem

        d = dict(src_dict)
        concurrent_vm_count = d.pop("concurrent_vm_count")

        concurrent_vm_limit = d.pop("concurrent_vm_limit")

        vms = []
        _vms = d.pop("vms")
        for vms_item_data in _vms:
            vms_item = VMListRunningVMsResponseDataVmsItem.from_dict(vms_item_data)

            vms.append(vms_item)

        vm_list_running_v_ms_response_data = cls(
            concurrent_vm_count=concurrent_vm_count,
            concurrent_vm_limit=concurrent_vm_limit,
            vms=vms,
        )

        vm_list_running_v_ms_response_data.additional_properties = d
        return vm_list_running_v_ms_response_data

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
