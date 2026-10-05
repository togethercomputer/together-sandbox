from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.sandbox_network import SandboxNetwork


T = TypeVar("T", bound="SandboxExperimental")


@_attrs_define
class SandboxExperimental:
    """Experimental features. Their API may change at short notice.

    Attributes:
        network (None | SandboxNetwork): The network policy, or null when the sandbox has none.
    """

    network: None | SandboxNetwork
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sandbox_network import SandboxNetwork

        network: dict[str, Any] | None
        if isinstance(self.network, SandboxNetwork):
            network = self.network.to_dict()
        else:
            network = self.network

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "network": network,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.sandbox_network import SandboxNetwork

        d = dict(src_dict)

        def _parse_network(data: object) -> None | SandboxNetwork:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                network_type_0 = SandboxNetwork.from_dict(data)

                return network_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SandboxNetwork, data)

        network = _parse_network(d.pop("network"))

        sandbox_experimental = cls(
            network=network,
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
