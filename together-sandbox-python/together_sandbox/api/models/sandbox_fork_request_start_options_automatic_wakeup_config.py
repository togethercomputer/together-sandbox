from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SandboxForkRequestStartOptionsAutomaticWakeupConfig")


@_attrs_define
class SandboxForkRequestStartOptionsAutomaticWakeupConfig:
    """Configuration for when the VM should automatically wake up from hibernation

    Attributes:
        http (bool | Unset): Whether the VM should automatically wake up on HTTP requests (excludes WebSocket requests)
            Default: True.
        websocket (bool | Unset): Whether the VM should automatically wake up on WebSocket connections Default: False.
    """

    http: bool | Unset = True
    websocket: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        http = self.http

        websocket = self.websocket

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if http is not UNSET:
            field_dict["http"] = http
        if websocket is not UNSET:
            field_dict["websocket"] = websocket

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        http = d.pop("http", UNSET)

        websocket = d.pop("websocket", UNSET)

        sandbox_fork_request_start_options_automatic_wakeup_config = cls(
            http=http,
            websocket=websocket,
        )

        sandbox_fork_request_start_options_automatic_wakeup_config.additional_properties = d
        return sandbox_fork_request_start_options_automatic_wakeup_config

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
