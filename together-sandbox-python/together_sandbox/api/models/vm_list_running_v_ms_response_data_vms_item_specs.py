from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VMListRunningVMsResponseDataVmsItemSpecs")


@_attrs_define
class VMListRunningVMsResponseDataVmsItemSpecs:
    """
    Attributes:
        cpu (int | Unset):
        memory (int | Unset):
        storage (int | Unset):
    """

    cpu: int | Unset = UNSET
    memory: int | Unset = UNSET
    storage: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cpu = self.cpu

        memory = self.memory

        storage = self.storage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cpu is not UNSET:
            field_dict["cpu"] = cpu
        if memory is not UNSET:
            field_dict["memory"] = memory
        if storage is not UNSET:
            field_dict["storage"] = storage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cpu = d.pop("cpu", UNSET)

        memory = d.pop("memory", UNSET)

        storage = d.pop("storage", UNSET)

        vm_list_running_v_ms_response_data_vms_item_specs = cls(
            cpu=cpu,
            memory=memory,
            storage=storage,
        )

        vm_list_running_v_ms_response_data_vms_item_specs.additional_properties = d
        return vm_list_running_v_ms_response_data_vms_item_specs

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
