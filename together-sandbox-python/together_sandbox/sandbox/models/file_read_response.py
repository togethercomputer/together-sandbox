from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.file_read_response_encoding import FileReadResponseEncoding

T = TypeVar("T", bound="FileReadResponse")


@_attrs_define
class FileReadResponse:
    """
    Attributes:
        path (str): File path
        content (str): File content
        encoding (FileReadResponseEncoding): Encoding of the content field
    """

    path: str
    content: str
    encoding: FileReadResponseEncoding
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        content = self.content

        encoding = self.encoding.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "content": content,
                "encoding": encoding,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        content = d.pop("content")

        encoding_value = d.pop("encoding", "utf-8")
        try:
            encoding = FileReadResponseEncoding(encoding_value)
        except ValueError:
            encoding = FileReadResponseEncoding("utf-8")

        file_read_response = cls(
            path=path,
            content=content,
            encoding=encoding,
        )

        file_read_response.additional_properties = d
        return file_read_response

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
