from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TaskRestart")


@_attrs_define
class TaskRestart:
    """
    Attributes:
        files (list[str]):
        clone (bool):
        resume (bool):
        branch (bool):
    """

    files: list[str]
    clone: bool
    resume: bool
    branch: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = self.files

        clone = self.clone

        resume = self.resume

        branch = self.branch

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
                "clone": clone,
                "resume": resume,
                "branch": branch,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        files = cast(list[str], d.pop("files"))

        clone = d.pop("clone")

        resume = d.pop("resume")

        branch = d.pop("branch")

        task_restart = cls(
            files=files,
            clone=clone,
            resume=resume,
            branch=branch,
        )

        task_restart.additional_properties = d
        return task_restart

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
