from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.billing_usage_line_item import BillingUsageLineItem


T = TypeVar("T", bound="BillingUsageWindow")


@_attrs_define
class BillingUsageWindow:
    """
    Attributes:
        date (str): The date of the time window, YYYY-MM-DD.
        start_time (datetime.datetime): Start of the time window (UTC, ISO 8601).
        end_time (datetime.datetime): Exclusive end of the time window (UTC, ISO 8601).
        line_items (list[BillingUsageLineItem]):
    """

    date: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    line_items: list[BillingUsageLineItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        start_time = self.start_time.isoformat()

        end_time = self.end_time.isoformat()

        line_items = []
        for line_items_item_data in self.line_items:
            line_items_item = line_items_item_data.to_dict()
            line_items.append(line_items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "line_items": line_items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.billing_usage_line_item import BillingUsageLineItem

        d = dict(src_dict)
        date = d.pop("date")

        start_time = isoparse(d.pop("start_time"))

        end_time = isoparse(d.pop("end_time"))

        line_items = []
        _line_items = d.pop("line_items")
        for line_items_item_data in _line_items:
            line_items_item = BillingUsageLineItem.from_dict(line_items_item_data)

            line_items.append(line_items_item)

        billing_usage_window = cls(
            date=date,
            start_time=start_time,
            end_time=end_time,
            line_items=line_items,
        )

        billing_usage_window.additional_properties = d
        return billing_usage_window

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
