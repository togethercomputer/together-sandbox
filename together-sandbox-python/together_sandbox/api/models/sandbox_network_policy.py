from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.inbound_rule import InboundRule


T = TypeVar("T", bound="SandboxNetworkPolicy")


@_attrs_define
class SandboxNetworkPolicy:
    """The sandbox's network policy.

    Attributes:
        inbound (list[InboundRule]):
        token (None | str): The token `allow_with_token` rules ask for in the `X-Sandbox-Token` header: the sandbox's
            agent token. Null unless the sandbox is running.
    """

    inbound: list[InboundRule]
    token: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inbound = []
        for inbound_item_data in self.inbound:
            inbound_item = inbound_item_data.to_dict()
            inbound.append(inbound_item)

        token: None | str
        token = self.token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inbound": inbound,
                "token": token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.inbound_rule import InboundRule

        d = dict(src_dict)
        inbound = []
        _inbound = d.pop("inbound")
        for inbound_item_data in _inbound:
            inbound_item = InboundRule.from_dict(inbound_item_data)

            inbound.append(inbound_item)

        def _parse_token(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        token = _parse_token(d.pop("token"))

        sandbox_network_policy = cls(
            inbound=inbound,
            token=token,
        )

        sandbox_network_policy.additional_properties = d
        return sandbox_network_policy

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
