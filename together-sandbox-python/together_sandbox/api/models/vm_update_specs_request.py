from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.vm_update_specs_request_tier import VMUpdateSpecsRequestTier

T = TypeVar("T", bound="VMUpdateSpecsRequest")


@_attrs_define
class VMUpdateSpecsRequest:
    """
    Attributes:
        tier (VMUpdateSpecsRequestTier): Determines which specs to update the VM with.

            Not all tiers will be available depending on the workspace subscription status, and higher tiers incur higher
            costs. Please see codesandbox.io/pricing for details on specs and costs.
             Example: Micro.
    """

    tier: VMUpdateSpecsRequestTier
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tier = self.tier.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tier": tier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tier = VMUpdateSpecsRequestTier(d.pop("tier"))

        vm_update_specs_request = cls(
            tier=tier,
        )

        vm_update_specs_request.additional_properties = d
        return vm_update_specs_request

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
