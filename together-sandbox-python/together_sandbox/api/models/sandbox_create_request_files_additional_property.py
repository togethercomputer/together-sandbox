from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SandboxCreateRequestFilesAdditionalProperty")


@_attrs_define
class SandboxCreateRequestFilesAdditionalProperty:
    """
    Attributes:
        binary_content (str | Unset): If the file has binary (non plain-text) contents, place the base-64 encoded
            contents in this key. Should be empty or missing if `is_binary` is `false`.
        code (str | Unset): If the file is non-binary in nature, place the (escaped) plain text contents in this key.
            Should be empty or missing if `is_binary` is `true`.
        is_binary (bool | Unset): Whether the file contains binary contents. Default: False.
    """

    binary_content: str | Unset = UNSET
    code: str | Unset = UNSET
    is_binary: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        binary_content = self.binary_content

        code = self.code

        is_binary = self.is_binary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if binary_content is not UNSET:
            field_dict["binary_content"] = binary_content
        if code is not UNSET:
            field_dict["code"] = code
        if is_binary is not UNSET:
            field_dict["is_binary"] = is_binary

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        binary_content = d.pop("binary_content", UNSET)

        code = d.pop("code", UNSET)

        is_binary = d.pop("is_binary", UNSET)

        sandbox_create_request_files_additional_property = cls(
            binary_content=binary_content,
            code=code,
            is_binary=is_binary,
        )

        sandbox_create_request_files_additional_property.additional_properties = d
        return sandbox_create_request_files_additional_property

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
