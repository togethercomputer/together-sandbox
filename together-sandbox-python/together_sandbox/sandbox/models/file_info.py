from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileInfo")


@_attrs_define
class FileInfo:
    """
    Attributes:
        name (str): File or directory name
        path (str): Full path to the file or directory
        is_dir (bool): Whether this entry is a directory
        size (int): File size in bytes
        mod_time (str): Last modification time
    """

    name: str
    path: str
    is_dir: bool
    size: int
    mod_time: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        path = self.path

        is_dir = self.is_dir

        size = self.size

        mod_time = self.mod_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "path": path,
                "isDir": is_dir,
                "size": size,
                "modTime": mod_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        path = d.pop("path")

        is_dir = d.pop("isDir")

        size = d.pop("size")

        mod_time = d.pop("modTime")

        file_info = cls(
            name=name,
            path=path,
            is_dir=is_dir,
            size=size,
            mod_time=mod_time,
        )

        file_info.additional_properties = d
        return file_info

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
