from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.network_policy import NetworkPolicy


T = TypeVar("T", bound="SandboxExperimental")


@_attrs_define
class SandboxExperimental:
    """Experimental features. Their API may change at short notice.

    Attributes:
        network_policy (NetworkPolicy | None | Unset): The network policy, or null when the sandbox has none.
    """

    network_policy: NetworkPolicy | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.network_policy import NetworkPolicy

        network_policy: dict[str, Any] | None | Unset
        if isinstance(self.network_policy, Unset):
            network_policy = UNSET
        elif isinstance(self.network_policy, NetworkPolicy):
            network_policy = self.network_policy.to_dict()
        else:
            network_policy = self.network_policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if network_policy is not UNSET:
            field_dict["network_policy"] = network_policy

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.network_policy import NetworkPolicy

        d = dict(src_dict)

        def _parse_network_policy(data: object) -> NetworkPolicy | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                network_policy_type_0 = NetworkPolicy.from_dict(data)

                return network_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(NetworkPolicy | None | Unset, data)

        network_policy = _parse_network_policy(d.pop("network_policy", UNSET))

        sandbox_experimental = cls(
            network_policy=network_policy,
        )

        sandbox_experimental.additional_properties = d
        return sandbox_experimental

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
