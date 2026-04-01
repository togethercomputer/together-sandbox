from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.vm_start_request_tier import VMStartRequestTier
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.vm_start_request_automatic_wakeup_config import (
        VMStartRequestAutomaticWakeupConfig,
    )


T = TypeVar("T", bound="VMStartRequest")


@_attrs_define
class VMStartRequest:
    """
    Attributes:
        automatic_wakeup_config (VMStartRequestAutomaticWakeupConfig | Unset): Configuration for when the VM should
            automatically wake up from hibernation
        hibernation_timeout_seconds (int | Unset): The time in seconds after which the VM will hibernate due to
            inactivity.
            Must be a positive integer between 1 and 86400 (24 hours).
            Defaults to 300 seconds (5 minutes) if not specified.
             Example: 300.
        ipcountry (str | Unset): This determines in which cluster, closest to the given country the VM will be started
            in. The format is ISO-3166-1 alpha-2. If not set, the VM will be started closest to the caller of this API. This
            will only be applied when a VM is run for the first time, and will only serve as a hint (e.g. if the template of
            this sandbox runs in EU cluster, this sandbox will also run in the EU cluster). Example: NL.
        tier (VMStartRequestTier | Unset): Determines which specs to start the VM with. If not specified, the VM will
            start with the default specs for the workspace.

            You can only specify a VM tier when starting a VM that is inside your workspace. Specifying a VM tier for
            someone else's sandbox will return an error.

            Not all tiers will be available depending on the workspace subscription status, and higher tiers incur higher
            costs. Please see codesandbox.io/pricing for details on specs and costs.
             Example: Micro.
    """

    automatic_wakeup_config: VMStartRequestAutomaticWakeupConfig | Unset = UNSET
    hibernation_timeout_seconds: int | Unset = UNSET
    ipcountry: str | Unset = UNSET
    tier: VMStartRequestTier | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        automatic_wakeup_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.automatic_wakeup_config, Unset):
            automatic_wakeup_config = self.automatic_wakeup_config.to_dict()

        hibernation_timeout_seconds = self.hibernation_timeout_seconds

        ipcountry = self.ipcountry

        tier: str | Unset = UNSET
        if not isinstance(self.tier, Unset):
            tier = self.tier.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if automatic_wakeup_config is not UNSET:
            field_dict["automatic_wakeup_config"] = automatic_wakeup_config
        if hibernation_timeout_seconds is not UNSET:
            field_dict["hibernation_timeout_seconds"] = hibernation_timeout_seconds
        if ipcountry is not UNSET:
            field_dict["ipcountry"] = ipcountry
        if tier is not UNSET:
            field_dict["tier"] = tier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vm_start_request_automatic_wakeup_config import (
            VMStartRequestAutomaticWakeupConfig,
        )

        d = dict(src_dict)
        _automatic_wakeup_config = d.pop("automatic_wakeup_config", UNSET)
        automatic_wakeup_config: VMStartRequestAutomaticWakeupConfig | Unset
        if isinstance(_automatic_wakeup_config, Unset):
            automatic_wakeup_config = UNSET
        else:
            automatic_wakeup_config = VMStartRequestAutomaticWakeupConfig.from_dict(
                _automatic_wakeup_config
            )

        hibernation_timeout_seconds = d.pop("hibernation_timeout_seconds", UNSET)

        ipcountry = d.pop("ipcountry", UNSET)

        _tier = d.pop("tier", UNSET)
        tier: VMStartRequestTier | Unset
        if isinstance(_tier, Unset):
            tier = UNSET
        else:
            tier = VMStartRequestTier(_tier)

        vm_start_request = cls(
            automatic_wakeup_config=automatic_wakeup_config,
            hibernation_timeout_seconds=hibernation_timeout_seconds,
            ipcountry=ipcountry,
            tier=tier,
        )

        vm_start_request.additional_properties = d
        return vm_start_request

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
