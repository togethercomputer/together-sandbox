from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tags import Tags


T = TypeVar("T", bound="TerminationSnapshot")


@_attrs_define
class TerminationSnapshot:
    """The snapshot captured when a sandbox terminates.

    Attributes:
        aliases (list[str] | Unset): Aliases to apply to the produced snapshot.
        ttl (int | Unset): Seconds after which the snapshot produced on termination expires. Must be > 0. Omit to keep
            the snapshot indefinitely.
        tags (Tags | Unset): User-defined key-value labels (both keys and values are strings).
    """

    aliases: list[str] | Unset = UNSET
    ttl: int | Unset = UNSET
    tags: Tags | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if ttl is not UNSET:
            field_dict["ttl"] = ttl
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.tags import Tags

        d = dict(src_dict)
        aliases = cast(list[str], d.pop("aliases", UNSET))

        ttl = d.pop("ttl", UNSET)

        _tags = d.pop("tags", UNSET)
        tags: Tags | Unset
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = Tags.from_dict(_tags)

        termination_snapshot = cls(
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
