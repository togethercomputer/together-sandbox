from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.termination_snapshot import TerminationSnapshot


T = TypeVar("T", bound="TerminateSandboxBody")


@_attrs_define
class TerminateSandboxBody:
    """
    Attributes:
        snapshot (None | TerminationSnapshot | Unset): What this teardown snapshots, overriding the snapshot the
            sandbox's stored termination policy would take. Omit to keep the stored policy; null makes the teardown
            ephemeral (no snapshot).
    """

    snapshot: None | TerminationSnapshot | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.termination_snapshot import TerminationSnapshot

        snapshot: dict[str, Any] | None | Unset
        if isinstance(self.snapshot, Unset):
            snapshot = UNSET
        elif isinstance(self.snapshot, TerminationSnapshot):
            snapshot = self.snapshot.to_dict()
        else:
            snapshot = self.snapshot

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if snapshot is not UNSET:
            field_dict["snapshot"] = snapshot

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.termination_snapshot import TerminationSnapshot

        d = dict(src_dict)

        def _parse_snapshot(data: object) -> None | TerminationSnapshot | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                snapshot_type_0 = TerminationSnapshot.from_dict(data)

                return snapshot_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TerminationSnapshot | Unset, data)

        snapshot = _parse_snapshot(d.pop("snapshot", UNSET))

        terminate_sandbox_body = cls(
            snapshot=snapshot,
        )

        terminate_sandbox_body.additional_properties = d
        return terminate_sandbox_body

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
