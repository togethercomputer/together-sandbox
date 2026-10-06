from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.inbound_rule_access import InboundRuleAccess
from ..types import UNSET, Unset

T = TypeVar("T", bound="InboundRule")


@_attrs_define
class InboundRule:
    """
    Attributes:
        from_ (list[str]): The clients the rule applies to: `*`, IPs, or CIDRs.
        access (InboundRuleAccess): `allow_with_token` admits a request only if it presents the sandbox's agent token
            (`agent.token`) in the `X-Sandbox-Token` header. The header is removed before the request reaches the sandbox.
        to_port (str | Unset): `*` (the default), a port, or an inclusive range `low-high`. No two rules may cover the
            same port, and only one may be `*`.
    """

    from_: list[str]
    access: InboundRuleAccess
    to_port: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from_ = self.from_

        access = self.access.value

        to_port = self.to_port

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "from": from_,
                "access": access,
            }
        )
        if to_port is not UNSET:
            field_dict["to_port"] = to_port

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        from_ = cast(list[str], d.pop("from"))

        access = InboundRuleAccess(d.pop("access"))

        to_port = d.pop("to_port", UNSET)

        inbound_rule = cls(
            from_=from_,
            access=access,
            to_port=to_port,
        )

        inbound_rule.additional_properties = d
        return inbound_rule

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
