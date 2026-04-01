from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.file_info import FileInfo


T = TypeVar("T", bound="DirectoryListResponse")


@_attrs_define
class DirectoryListResponse:
    """
    Attributes:
        path (str): Directory path
        files (list[FileInfo]): List of files and directories
    """

    path: str
    files: list[FileInfo]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_info import FileInfo

        d = dict(src_dict)
        path = d.pop("path")

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = FileInfo.from_dict(files_item_data)

            files.append(files_item)

        directory_list_response = cls(
            path=path,
            files=files,
        )

        directory_list_response.additional_properties = d
        return directory_list_response

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
