from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="AllowRule")


@_attrs_define
class AllowRule:
    """
    Attributes:
        ports (list[str]): The ports the rule admits requests to: ports, inclusive ranges `low-high`, or `*` for every
            port.
        from_ (list[str] | Unset): The clients the rule admits requests from: `*`, IPs, or CIDRs. Defaults to `["*"]`,
            every client.
        requires_token (bool | Unset): Admit a request only if it presents the sandbox's agent token (`agent.token`) in
            the `X-Sandbox-Token` header. The header is removed before the request reaches the sandbox.
             Default: False.
    """

    ports: list[str]
    from_: list[str] | Unset = UNSET
    requires_token: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ports = self.ports

        from_: list[str] | Unset = UNSET
        if not isinstance(self.from_, Unset):
            from_ = self.from_

        requires_token = self.requires_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ports": ports,
            }
        )
        if from_ is not UNSET:
            field_dict["from"] = from_
        if requires_token is not UNSET:
            field_dict["requires_token"] = requires_token

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ports = cast(list[str], d.pop("ports"))

        from_ = cast(list[str], d.pop("from", UNSET))

        requires_token = d.pop("requires_token", UNSET)

        allow_rule = cls(
            ports=ports,
            from_=from_,
            requires_token=requires_token,
        )

        allow_rule.additional_properties = d
        return allow_rule

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
