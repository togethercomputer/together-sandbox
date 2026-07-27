from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.termination_snapshot import TerminationSnapshot


T = TypeVar("T", bound="TerminationPolicy")


@_attrs_define
class TerminationPolicy:
    """The policy applied when a sandbox terminates.

    Attributes:
        snapshot (TerminationSnapshot): The snapshot captured when a sandbox terminates.
    """

    snapshot: TerminationSnapshot
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        snapshot = self.snapshot.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "snapshot": snapshot,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.termination_snapshot import TerminationSnapshot

        d = dict(src_dict)
        snapshot = TerminationSnapshot.from_dict(d.pop("snapshot"))

        termination_policy = cls(
            snapshot=snapshot,
        )

        termination_policy.additional_properties = d
        return termination_policy

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
