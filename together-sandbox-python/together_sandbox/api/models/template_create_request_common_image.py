from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TemplateCreateRequestCommonImage")


@_attrs_define
class TemplateCreateRequestCommonImage:
    """Container image to use as template

    Attributes:
        name (str): The image name (for example 'nginx').
        architecture (str | Unset): The architecture of the image. Required for multi-platform images
        registry (str | Unset): The container registry where the image is stored. Default: 'docker.io'.
        repository (str | Unset): The repository or namespace where the image is stored. Default: 'library'.
        tag (str | Unset): The image tag. Default: 'latest'.
    """

    name: str
    architecture: str | Unset = UNSET
    registry: str | Unset = "docker.io"
    repository: str | Unset = "library"
    tag: str | Unset = "latest"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        architecture = self.architecture

        registry = self.registry

        repository = self.repository

        tag = self.tag

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if architecture is not UNSET:
            field_dict["architecture"] = architecture
        if registry is not UNSET:
            field_dict["registry"] = registry
        if repository is not UNSET:
            field_dict["repository"] = repository
        if tag is not UNSET:
            field_dict["tag"] = tag

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        architecture = d.pop("architecture", UNSET)

        registry = d.pop("registry", UNSET)

        repository = d.pop("repository", UNSET)

        tag = d.pop("tag", UNSET)

        template_create_request_common_image = cls(
            name=name,
            architecture=architecture,
            registry=registry,
            repository=repository,
            tag=tag,
        )

        template_create_request_common_image.additional_properties = d
        return template_create_request_common_image

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
