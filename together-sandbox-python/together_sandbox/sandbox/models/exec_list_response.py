from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.exec_item import ExecItem


T = TypeVar("T", bound="ExecListResponse")


@_attrs_define
class ExecListResponse:
    """
    Attributes:
        execs (list[ExecItem]): List of execs
    """

    execs: list[ExecItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        execs = []
        for execs_item_data in self.execs:
            execs_item = execs_item_data.to_dict()
            execs.append(execs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "execs": execs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.exec_item import ExecItem

        d = dict(src_dict)
        execs = []
        _execs = d.pop("execs")
        for execs_item_data in _execs:
            execs_item = ExecItem.from_dict(execs_item_data)

            execs.append(execs_item)

        exec_list_response = cls(
            execs=execs,
        )

        exec_list_response.additional_properties = d
        return exec_list_response

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
