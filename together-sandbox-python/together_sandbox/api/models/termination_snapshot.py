from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.termination_snapshot_tags import TerminationSnapshotTags


T = TypeVar("T", bound="TerminationSnapshot")


@_attrs_define
class TerminationSnapshot:
    """The snapshot produced when a sandbox terminates.

    Attributes:
        memory (bool | Unset): Whether to include a memory snapshot in addition to the filesystem. Default: False.
        aliases (list[str] | Unset): Aliases to apply to the produced snapshot.
        ttl (int | Unset): Seconds after creation before the produced snapshot is automatically deleted.
        tags (TerminationSnapshotTags | Unset): Arbitrary key/value labels to attach to the produced snapshot.
    """

    memory: bool | Unset = False
    aliases: list[str] | Unset = UNSET
    ttl: int | Unset = UNSET
    tags: TerminationSnapshotTags | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        memory = self.memory

        aliases: list[str] | Unset = UNSET
        if not isinstance(self.aliases, Unset):
            aliases = self.aliases

        ttl = self.ttl

        tags: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if memory is not UNSET:
            field_dict["memory"] = memory
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if ttl is not UNSET:
            field_dict["ttl"] = ttl
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.termination_snapshot_tags import TerminationSnapshotTags

        d = dict(src_dict)
        memory = d.pop("memory", UNSET)

        aliases = cast(list[str], d.pop("aliases", UNSET))

        ttl = d.pop("ttl", UNSET)

        _tags = d.pop("tags", UNSET)
        tags: TerminationSnapshotTags | Unset
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = TerminationSnapshotTags.from_dict(_tags)

        termination_snapshot = cls(
            memory=memory,
            aliases=aliases,
            ttl=ttl,
            tags=tags,
        )

        termination_snapshot.additional_properties = d
        return termination_snapshot

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
