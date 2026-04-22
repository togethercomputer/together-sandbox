from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_snapshot_body_image import CreateSnapshotBodyImage


T = TypeVar("T", bound="CreateSnapshotBody")


@_attrs_define
class CreateSnapshotBody:
    """
    Attributes:
        image (CreateSnapshotBodyImage):
    """

    image: CreateSnapshotBodyImage
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        image = self.image.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "image": image,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_snapshot_body_image import CreateSnapshotBodyImage

        d = dict(src_dict)
        image = CreateSnapshotBodyImage.from_dict(d.pop("image"))

        create_snapshot_body = cls(
            image=image,
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
