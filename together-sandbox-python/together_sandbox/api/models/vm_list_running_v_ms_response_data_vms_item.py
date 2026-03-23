from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.vm_list_running_v_ms_response_data_vms_item_specs import (
        VMListRunningVMsResponseDataVmsItemSpecs,
    )


T = TypeVar("T", bound="VMListRunningVMsResponseDataVmsItem")


@_attrs_define
class VMListRunningVMsResponseDataVmsItem:
    """
    Attributes:
        credit_basis (str | Unset):
        id (str | Unset):
        last_active_at (datetime.datetime | Unset):
        session_started_at (datetime.datetime | Unset):
        specs (VMListRunningVMsResponseDataVmsItemSpecs | Unset):
    """

    credit_basis: str | Unset = UNSET
    id: str | Unset = UNSET
    last_active_at: datetime.datetime | Unset = UNSET
    session_started_at: datetime.datetime | Unset = UNSET
    specs: VMListRunningVMsResponseDataVmsItemSpecs | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        credit_basis = self.credit_basis

        id = self.id

        last_active_at: str | Unset = UNSET
        if not isinstance(self.last_active_at, Unset):
            last_active_at = self.last_active_at.isoformat()

        session_started_at: str | Unset = UNSET
        if not isinstance(self.session_started_at, Unset):
            session_started_at = self.session_started_at.isoformat()

        specs: dict[str, Any] | Unset = UNSET
        if not isinstance(self.specs, Unset):
            specs = self.specs.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if credit_basis is not UNSET:
            field_dict["credit_basis"] = credit_basis
        if id is not UNSET:
            field_dict["id"] = id
        if last_active_at is not UNSET:
            field_dict["last_active_at"] = last_active_at
        if session_started_at is not UNSET:
            field_dict["session_started_at"] = session_started_at
        if specs is not UNSET:
            field_dict["specs"] = specs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vm_list_running_v_ms_response_data_vms_item_specs import (
            VMListRunningVMsResponseDataVmsItemSpecs,
        )

        d = dict(src_dict)
        credit_basis = d.pop("credit_basis", UNSET)

        id = d.pop("id", UNSET)

        _last_active_at = d.pop("last_active_at", UNSET)
        last_active_at: datetime.datetime | Unset
        if isinstance(_last_active_at, Unset):
            last_active_at = UNSET
        else:
            last_active_at = isoparse(_last_active_at)

        _session_started_at = d.pop("session_started_at", UNSET)
        session_started_at: datetime.datetime | Unset
        if isinstance(_session_started_at, Unset):
            session_started_at = UNSET
        else:
            session_started_at = isoparse(_session_started_at)

        _specs = d.pop("specs", UNSET)
        specs: VMListRunningVMsResponseDataVmsItemSpecs | Unset
        if isinstance(_specs, Unset):
            specs = UNSET
        else:
            specs = VMListRunningVMsResponseDataVmsItemSpecs.from_dict(_specs)

        vm_list_running_v_ms_response_data_vms_item = cls(
            credit_basis=credit_basis,
            id=id,
            last_active_at=last_active_at,
            session_started_at=session_started_at,
            specs=specs,
        )

        vm_list_running_v_ms_response_data_vms_item.additional_properties = d
        return vm_list_running_v_ms_response_data_vms_item

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
