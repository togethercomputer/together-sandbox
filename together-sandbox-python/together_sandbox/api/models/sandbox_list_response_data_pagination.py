from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SandboxListResponseDataPagination")


@_attrs_define
class SandboxListResponseDataPagination:
    """
    Attributes:
        current_page (int):
        next_page (int | None): The number of the next page, if any. If `null`, the current page is the last page of
            records.
        total_records (int):
    """

    current_page: int
    next_page: int | None
    total_records: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        current_page = self.current_page

        next_page: int | None
        next_page = self.next_page

        total_records = self.total_records

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "current_page": current_page,
                "next_page": next_page,
                "total_records": total_records,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_page = d.pop("current_page")

        def _parse_next_page(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        next_page = _parse_next_page(d.pop("next_page"))

        total_records = d.pop("total_records")

        sandbox_list_response_data_pagination = cls(
            current_page=current_page,
            next_page=next_page,
            total_records=total_records,
        )

        sandbox_list_response_data_pagination.additional_properties = d
        return sandbox_list_response_data_pagination

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
