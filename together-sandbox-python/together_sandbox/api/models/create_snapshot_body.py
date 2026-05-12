from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_snapshot_body_architecture import CreateSnapshotBodyArchitecture
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSnapshotBody")


@_attrs_define
class CreateSnapshotBody:
    """
    Attributes:
        image (str): Container image reference. Parsed as `[registry/][repository/]name[:tag]`, using Docker Hub and
            `latest` as defaults when omitted.
        architecture (CreateSnapshotBodyArchitecture | Unset): Expected image architecture.
    """

    image: str
    architecture: CreateSnapshotBodyArchitecture | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        image = self.image

        architecture: str | Unset = UNSET
        if not isinstance(self.architecture, Unset):
            architecture = self.architecture.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "image": image,
            }
        )
        if architecture is not UNSET:
            field_dict["architecture"] = architecture

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        image = d.pop("image")

        _architecture = d.pop("architecture", UNSET)
        architecture: CreateSnapshotBodyArchitecture | Unset
        if isinstance(_architecture, Unset):
            architecture = UNSET
        else:
            architecture = CreateSnapshotBodyArchitecture(_architecture)

        create_snapshot_body = cls(
            image=image,
            architecture=architecture,
        )

        create_snapshot_body.additional_properties = d
        return create_snapshot_body

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
