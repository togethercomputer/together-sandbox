from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.file_action_request_action import FileActionRequestAction

T = TypeVar("T", bound="FileActionRequest")


@_attrs_define
class FileActionRequest:
    """
    Attributes:
        action (FileActionRequestAction): Type of action to perform on the file
        destination (str): Destination path for move operation
    """

    action: FileActionRequestAction
    destination: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action.value

        destination = self.destination

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
                "destination": destination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action = FileActionRequestAction(d.pop("action"))

        destination = d.pop("destination")

        file_action_request = cls(
            action=action,
            destination=destination,
        )

        file_action_request.additional_properties = d
        return file_action_request

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
