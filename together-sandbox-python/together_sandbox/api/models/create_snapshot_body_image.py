from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_snapshot_body_image_architecture import (
    CreateSnapshotBodyImageArchitecture,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSnapshotBodyImage")


@_attrs_define
class CreateSnapshotBodyImage:
    """
    Attributes:
        name (str):
        registry (str | Unset):
        repository (str | Unset):
        tag (str | Unset):
        architecture (CreateSnapshotBodyImageArchitecture | Unset):
    """

    name: str
    registry: str | Unset = UNSET
    repository: str | Unset = UNSET
    tag: str | Unset = UNSET
    architecture: CreateSnapshotBodyImageArchitecture | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        registry = self.registry

        repository = self.repository

        tag = self.tag

        architecture: str | Unset = UNSET
        if not isinstance(self.architecture, Unset):
            architecture = self.architecture.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if registry is not UNSET:
            field_dict["registry"] = registry
        if repository is not UNSET:
            field_dict["repository"] = repository
        if tag is not UNSET:
            field_dict["tag"] = tag
        if architecture is not UNSET:
            field_dict["architecture"] = architecture

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        registry = d.pop("registry", UNSET)

        repository = d.pop("repository", UNSET)

        tag = d.pop("tag", UNSET)

        _architecture = d.pop("architecture", UNSET)
        architecture: CreateSnapshotBodyImageArchitecture | Unset
        if isinstance(_architecture, Unset):
            architecture = UNSET
        else:
            architecture = CreateSnapshotBodyImageArchitecture(_architecture)

        create_snapshot_body_image = cls(
            name=name,
            registry=registry,
            repository=repository,
            tag=tag,
            architecture=architecture,
        )

        create_snapshot_body_image.additional_properties = d
        return create_snapshot_body_image

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
