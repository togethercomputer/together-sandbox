from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.meta_information_api import MetaInformationApi
    from ..models.meta_information_auth import MetaInformationAuth
    from ..models.meta_information_rate_limits import MetaInformationRateLimits


T = TypeVar("T", bound="MetaInformation")


@_attrs_define
class MetaInformation:
    """
    Attributes:
        api (MetaInformationApi): Meta information about the CodeSandbox API
        auth (MetaInformationAuth | Unset): Meta information about the current authentication context
        rate_limits (MetaInformationRateLimits | Unset): Current workspace rate limits
    """

    api: MetaInformationApi
    auth: MetaInformationAuth | Unset = UNSET
    rate_limits: MetaInformationRateLimits | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api = self.api.to_dict()

        auth: dict[str, Any] | Unset = UNSET
        if not isinstance(self.auth, Unset):
            auth = self.auth.to_dict()

        rate_limits: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rate_limits, Unset):
            rate_limits = self.rate_limits.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "api": api,
            }
        )
        if auth is not UNSET:
            field_dict["auth"] = auth
        if rate_limits is not UNSET:
            field_dict["rate_limits"] = rate_limits

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.meta_information_api import MetaInformationApi
        from ..models.meta_information_auth import MetaInformationAuth
        from ..models.meta_information_rate_limits import MetaInformationRateLimits

        d = dict(src_dict)
        api = MetaInformationApi.from_dict(d.pop("api"))

        _auth = d.pop("auth", UNSET)
        auth: MetaInformationAuth | Unset
        if isinstance(_auth, Unset):
            auth = UNSET
        else:
            auth = MetaInformationAuth.from_dict(_auth)

        _rate_limits = d.pop("rate_limits", UNSET)
        rate_limits: MetaInformationRateLimits | Unset
        if isinstance(_rate_limits, Unset):
            rate_limits = UNSET
        else:
            rate_limits = MetaInformationRateLimits.from_dict(_rate_limits)

        meta_information = cls(
            api=api,
            auth=auth,
            rate_limits=rate_limits,
        )

        meta_information.additional_properties = d
        return meta_information

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
