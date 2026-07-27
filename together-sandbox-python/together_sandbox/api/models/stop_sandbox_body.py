from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.stop_sandbox_body_stop_type import StopSandboxBodyStopType
from ..types import UNSET, Unset

T = TypeVar("T", bound="StopSandboxBody")


@_attrs_define
class StopSandboxBody:
    """
    Attributes:
        stop_type (StopSandboxBodyStopType | Unset): How to stop the sandbox. Default: StopSandboxBodyStopType.SHUTDOWN.
    """

    stop_type: StopSandboxBodyStopType | Unset = StopSandboxBodyStopType.SHUTDOWN
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stop_type: str | Unset = UNSET
        if not isinstance(self.stop_type, Unset):
            stop_type = self.stop_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if stop_type is not UNSET:
            field_dict["stop_type"] = stop_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _stop_type = d.pop("stop_type", UNSET)
        stop_type: StopSandboxBodyStopType | Unset
        if isinstance(_stop_type, Unset):
            stop_type = UNSET
        else:
            stop_type = StopSandboxBodyStopType(_stop_type)

        stop_sandbox_body = cls(
            stop_type=stop_type,
        )

        stop_sandbox_body.additional_properties = d
        return stop_sandbox_body

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
