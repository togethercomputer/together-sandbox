from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.meta_information_rate_limits_concurrent_vms import MetaInformationRateLimitsConcurrentVms
    from ..models.meta_information_rate_limits_requests_hourly import MetaInformationRateLimitsRequestsHourly
    from ..models.meta_information_rate_limits_sandboxes_hourly import MetaInformationRateLimitsSandboxesHourly


T = TypeVar("T", bound="MetaInformationRateLimits")


@_attrs_define
class MetaInformationRateLimits:
    """Current workspace rate limits

    Attributes:
        concurrent_vms (MetaInformationRateLimitsConcurrentVms):
        requests_hourly (MetaInformationRateLimitsRequestsHourly):
        sandboxes_hourly (MetaInformationRateLimitsSandboxesHourly):
    """

    concurrent_vms: MetaInformationRateLimitsConcurrentVms
    requests_hourly: MetaInformationRateLimitsRequestsHourly
    sandboxes_hourly: MetaInformationRateLimitsSandboxesHourly
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        concurrent_vms = self.concurrent_vms.to_dict()

        requests_hourly = self.requests_hourly.to_dict()

        sandboxes_hourly = self.sandboxes_hourly.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "concurrent_vms": concurrent_vms,
                "requests_hourly": requests_hourly,
                "sandboxes_hourly": sandboxes_hourly,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.meta_information_rate_limits_concurrent_vms import MetaInformationRateLimitsConcurrentVms
        from ..models.meta_information_rate_limits_requests_hourly import MetaInformationRateLimitsRequestsHourly
        from ..models.meta_information_rate_limits_sandboxes_hourly import MetaInformationRateLimitsSandboxesHourly

        d = dict(src_dict)
        concurrent_vms = MetaInformationRateLimitsConcurrentVms.from_dict(d.pop("concurrent_vms"))

        requests_hourly = MetaInformationRateLimitsRequestsHourly.from_dict(d.pop("requests_hourly"))

        sandboxes_hourly = MetaInformationRateLimitsSandboxesHourly.from_dict(d.pop("sandboxes_hourly"))

        meta_information_rate_limits = cls(
            concurrent_vms=concurrent_vms,
            requests_hourly=requests_hourly,
            sandboxes_hourly=sandboxes_hourly,
        )

        meta_information_rate_limits.additional_properties = d
        return meta_information_rate_limits

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
