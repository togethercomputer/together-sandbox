from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.template_create_request_common_image import (
        TemplateCreateRequestCommonImage,
    )


T = TypeVar("T", bound="TemplateCreateRequestCommon")


@_attrs_define
class TemplateCreateRequestCommon:
    """
    Attributes:
        fork_of (str): Short ID of the sandbox to fork. Example: pt_1234567890.
        description (str | Unset): Template description. Maximum 255 characters. Defaults to description of original
            sandbox. Default: '[Template description]'.
        image (TemplateCreateRequestCommonImage | Unset): Container image to use as template
        tags (list[str] | Unset): Tags to set on the new sandbox, if any. Will not inherit tags from the source sandbox.
        title (str | Unset): Template title. Maximum 255 characters. Defaults to title of original sandbox with
            (forked). Default: '[Template title]'.
    """

    fork_of: str
    description: str | Unset = "[Template description]"
    image: TemplateCreateRequestCommonImage | Unset = UNSET
    tags: list[str] | Unset = UNSET
    title: str | Unset = "[Template title]"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fork_of = self.fork_of

        description = self.description

        image: dict[str, Any] | Unset = UNSET
        if not isinstance(self.image, Unset):
            image = self.image.to_dict()

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "forkOf": fork_of,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if image is not UNSET:
            field_dict["image"] = image
        if tags is not UNSET:
            field_dict["tags"] = tags
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.template_create_request_common_image import (
            TemplateCreateRequestCommonImage,
        )

        d = dict(src_dict)
        fork_of = d.pop("forkOf")

        description = d.pop("description", UNSET)

        _image = d.pop("image", UNSET)
        image: TemplateCreateRequestCommonImage | Unset
        if isinstance(_image, Unset):
            image = UNSET
        else:
            image = TemplateCreateRequestCommonImage.from_dict(_image)

        tags = cast(list[str], d.pop("tags", UNSET))

        title = d.pop("title", UNSET)

        template_create_request_common = cls(
            fork_of=fork_of,
            description=description,
            image=image,
            tags=tags,
            title=title,
        )

        template_create_request_common.additional_properties = d
        return template_create_request_common

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
