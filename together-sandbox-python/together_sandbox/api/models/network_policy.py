from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.allow_rule import AllowRule


T = TypeVar("T", bound="NetworkPolicy")


@_attrs_define
class NetworkPolicy:
    """Who may reach the sandbox through its URL. Without a network policy, a sandbox can be reached on every port. With
    one, every inbound request is blocked except those its `inbound_allowlist` admits: a request is admitted when a rule
    covers its port and its client. Rules can overlap; if any rule covering a request has `requires_token`, the request
    must present the token, even where another covering rule needs none. An empty allowlist admits nothing. Outbound
    rules are not supported yet.

    The sandbox's agent port (57468, which the SDKs and the agent URL use) is never filtered; the agent authenticates
    every request itself.

        Attributes:
            inbound_allowlist (list[AllowRule] | Unset):
    """

    inbound_allowlist: list[AllowRule] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        inbound_allowlist: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.inbound_allowlist, Unset):
            inbound_allowlist = []
            for inbound_allowlist_item_data in self.inbound_allowlist:
                inbound_allowlist_item = inbound_allowlist_item_data.to_dict()
                inbound_allowlist.append(inbound_allowlist_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if inbound_allowlist is not UNSET:
            field_dict["inbound_allowlist"] = inbound_allowlist

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.allow_rule import AllowRule

        d = dict(src_dict)
        _inbound_allowlist = d.pop("inbound_allowlist", UNSET)
        inbound_allowlist: list[AllowRule] | Unset = UNSET
        if _inbound_allowlist is not UNSET:
            inbound_allowlist = []
            for inbound_allowlist_item_data in _inbound_allowlist:
                inbound_allowlist_item = AllowRule.from_dict(
                    inbound_allowlist_item_data
                )

                inbound_allowlist.append(inbound_allowlist_item)

        network_policy = cls(
            inbound_allowlist=inbound_allowlist,
        )

        return network_policy
