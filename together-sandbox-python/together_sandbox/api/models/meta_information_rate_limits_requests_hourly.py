from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MetaInformationRateLimitsRequestsHourly")


@_attrs_define
class MetaInformationRateLimitsRequestsHourly:
    """
    Attributes:
        limit (int | Unset):
        remaining (int | Unset):
        reset (int | Unset):
    """

    limit: int | Unset = UNSET
    remaining: int | Unset = UNSET
    reset: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        remaining = self.remaining

        reset = self.reset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if limit is not UNSET:
            field_dict["limit"] = limit
        if remaining is not UNSET:
            field_dict["remaining"] = remaining
        if reset is not UNSET:
            field_dict["reset"] = reset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        limit = d.pop("limit", UNSET)

        remaining = d.pop("remaining", UNSET)

        reset = d.pop("reset", UNSET)

        meta_information_rate_limits_requests_hourly = cls(
            limit=limit,
            remaining=remaining,
            reset=reset,
        )

        meta_information_rate_limits_requests_hourly.additional_properties = d
        return meta_information_rate_limits_requests_hourly

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
