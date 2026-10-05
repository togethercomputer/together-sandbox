from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbound_rule import InboundRule


T = TypeVar("T", bound="NetworkPolicy")


@_attrs_define
class NetworkPolicy:
    """Who may reach the sandbox. Inbound applies to requests reaching the sandbox's URL, matched by port and by the
    client's address. Outbound rules are not supported yet.

    A port has at most one rule, and at most one rule applies to every port (`to_port` `*`). A request to a port is
    decided by that port's rule if the client is in its `from`, otherwise by the `*` rule if the client is in its
    `from`, otherwise it is allowed.

    The sandbox's agent port (57468, which the SDKs and the agent URL use) can be narrowed but never closed by accident:
    only a rule naming that port alone applies to it, never the `*` rule or a range. If that rule is `allow` or
    `allow_with_token`, clients outside its `from` are denied.

        Attributes:
            inbound (list[InboundRule] | Unset):
    """

    inbound: list[InboundRule] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        inbound: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.inbound, Unset):
            inbound = []
            for inbound_item_data in self.inbound:
                inbound_item = inbound_item_data.to_dict()
                inbound.append(inbound_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if inbound is not UNSET:
            field_dict["inbound"] = inbound

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.inbound_rule import InboundRule

        d = dict(src_dict)
        _inbound = d.pop("inbound", UNSET)
        inbound: list[InboundRule] | Unset = UNSET
        if _inbound is not UNSET:
            inbound = []
            for inbound_item_data in _inbound:
                inbound_item = InboundRule.from_dict(inbound_item_data)

                inbound.append(inbound_item)

        network_policy = cls(
            inbound=inbound,
        )

        return network_policy
