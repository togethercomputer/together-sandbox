from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.network_policy import NetworkPolicy


T = TypeVar("T", bound="CreateSandboxExperimental")


@_attrs_define
class CreateSandboxExperimental:
    """Experimental features. Their API may change at short notice.

    Attributes:
        network_policy (NetworkPolicy | Unset): Who may reach the sandbox through its URL. Without a network policy, a
            sandbox can be reached on every port. With one, every inbound request is blocked except those its
            `inbound_allowlist` admits: a request is admitted when a rule covers its port and its client. Rules can overlap;
            if any rule covering a request has `requires_token`, the request must present the token, even where another
            covering rule needs none. An empty allowlist admits nothing. Outbound rules are not supported yet.

            The sandbox's agent port (57468, which the SDKs and the agent URL use) is never filtered; the agent
            authenticates every request itself.
    """

    network_policy: NetworkPolicy | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        network_policy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.network_policy, Unset):
            network_policy = self.network_policy.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if network_policy is not UNSET:
            field_dict["network_policy"] = network_policy

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.network_policy import NetworkPolicy

        d = dict(src_dict)
        _network_policy = d.pop("network_policy", UNSET)
        network_policy: NetworkPolicy | Unset
        if isinstance(_network_policy, Unset):
            network_policy = UNSET
        else:
            network_policy = NetworkPolicy.from_dict(_network_policy)

        create_sandbox_experimental = cls(
            network_policy=network_policy,
        )

        return create_sandbox_experimental
