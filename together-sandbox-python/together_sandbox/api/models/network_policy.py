from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.egress_rule import EgressRule
    from ..models.ingress_rule import IngressRule


T = TypeVar("T", bound="NetworkPolicy")


@_attrs_define
class NetworkPolicy:
    """Who may reach the sandbox, and what it may reach. Rules are unordered: when several match, the most specific
    decides, and between equally specific rules the more restrictive one does. A host name is more specific than any
    address, a longer prefix or suffix more than a shorter one, and only then does the port count: a single port over a
    range, a narrower range over a wider one, either over `*`. A connection no rule matches is allowed.

    Ingress applies to requests reaching the sandbox's URL, matched by the client's address. Egress applies to every TCP
    connection the sandbox opens; host rules are matched against TLS SNI or the HTTP Host header, and a connection
    allowed by one is dialled to that host, never to the address the sandbox chose. A sandbox with any egress `deny`
    rule may send no UDP other than DNS. Whatever the policy, a sandbox can never reach private ranges or the cloud
    metadata service.

    The sandbox's agent port (57468, which the SDKs and the agent URL use) can be narrowed but never closed. Only
    ingress rules that name that port alone and a specific IP or CIDR apply to it; a `*` port, a range, or a `*` client
    never does. Those rules are an allow-list: if any of them admits clients, every client none of them matches is
    denied.

        Attributes:
            ingress (list[IngressRule] | Unset):
            egress (list[EgressRule] | Unset):
    """

    ingress: list[IngressRule] | Unset = UNSET
    egress: list[EgressRule] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ingress: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ingress, Unset):
            ingress = []
            for ingress_item_data in self.ingress:
                ingress_item = ingress_item_data.to_dict()
                ingress.append(ingress_item)

        egress: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.egress, Unset):
            egress = []
            for egress_item_data in self.egress:
                egress_item = egress_item_data.to_dict()
                egress.append(egress_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ingress is not UNSET:
            field_dict["ingress"] = ingress
        if egress is not UNSET:
            field_dict["egress"] = egress

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.egress_rule import EgressRule
        from ..models.ingress_rule import IngressRule

        d = dict(src_dict)
        _ingress = d.pop("ingress", UNSET)
        ingress: list[IngressRule] | Unset = UNSET
        if _ingress is not UNSET:
            ingress = []
            for ingress_item_data in _ingress:
                ingress_item = IngressRule.from_dict(ingress_item_data)

                ingress.append(ingress_item)

        _egress = d.pop("egress", UNSET)
        egress: list[EgressRule] | Unset = UNSET
        if _egress is not UNSET:
            egress = []
            for egress_item_data in _egress:
                egress_item = EgressRule.from_dict(egress_item_data)

                egress.append(egress_item)

        network_policy = cls(
            ingress=ingress,
            egress=egress,
        )

        network_policy.additional_properties = d
        return network_policy

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
