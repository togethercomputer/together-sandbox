from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.sandbox import Sandbox
    from ..models.sandbox_list_response_data_pagination import (
        SandboxListResponseDataPagination,
    )


T = TypeVar("T", bound="SandboxListResponseData")


@_attrs_define
class SandboxListResponseData:
    """
    Attributes:
        pagination (SandboxListResponseDataPagination):
        sandboxes (list[Sandbox]):
    """

    pagination: SandboxListResponseDataPagination
    sandboxes: list[Sandbox]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pagination = self.pagination.to_dict()

        sandboxes = []
        for sandboxes_item_data in self.sandboxes:
            sandboxes_item = sandboxes_item_data.to_dict()
            sandboxes.append(sandboxes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pagination": pagination,
                "sandboxes": sandboxes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sandbox import Sandbox
        from ..models.sandbox_list_response_data_pagination import (
            SandboxListResponseDataPagination,
        )

        d = dict(src_dict)
        pagination = SandboxListResponseDataPagination.from_dict(d.pop("pagination"))

        sandboxes = []
        _sandboxes = d.pop("sandboxes")
        for sandboxes_item_data in _sandboxes:
            sandboxes_item = Sandbox.from_dict(sandboxes_item_data)

            sandboxes.append(sandboxes_item)

        sandbox_list_response_data = cls(
            pagination=pagination,
            sandboxes=sandboxes,
        )

        sandbox_list_response_data.additional_properties = d
        return sandbox_list_response_data

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
