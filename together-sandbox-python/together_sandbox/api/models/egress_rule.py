from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.egress_rule_access import EgressRuleAccess
from ..types import UNSET, Unset

T = TypeVar("T", bound="EgressRule")


@_attrs_define
class EgressRule:
    """
    Attributes:
        to (str): `*`, an IP, a CIDR, a host name, or `*.domain`, which matches names under the domain but not the
            domain itself.
        access (EgressRuleAccess):
        to_port (str | Unset): `*` (the default), a port, or an inclusive range `low-high`.
    """

    to: str
    access: EgressRuleAccess
    to_port: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        to = self.to

        access = self.access.value

        to_port = self.to_port

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "to": to,
                "access": access,
            }
        )
        if to_port is not UNSET:
            field_dict["to_port"] = to_port

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        to = d.pop("to")

        access = EgressRuleAccess(d.pop("access"))

        to_port = d.pop("to_port", UNSET)

        egress_rule = cls(
            to=to,
            access=access,
            to_port=to_port,
        )

        egress_rule.additional_properties = d
        return egress_rule

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
