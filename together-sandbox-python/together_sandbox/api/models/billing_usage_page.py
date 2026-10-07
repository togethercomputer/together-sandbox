from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.billing_usage_page_currency import BillingUsagePageCurrency
from ..models.billing_usage_page_object import BillingUsagePageObject

if TYPE_CHECKING:
    from ..models.billing_usage_window import BillingUsageWindow


T = TypeVar("T", bound="BillingUsagePage")


@_attrs_define
class BillingUsagePage:
    """
    Attributes:
        object_ (BillingUsagePageObject):
        organization_id (str): The organization the usage belongs to, resolved from the API key.
        billing_period (str): The billing month, YYYY-MM.
        earliest_window_start (datetime.datetime | None): Start of the earliest time window with usage in the month
            (UTC, ISO 8601), or null when the month has no usage. Describes the whole month, not the current page.
        latest_window_end (datetime.datetime | None): Exclusive end of the latest time window with usage in the month
            (UTC, ISO 8601), or null when the month has no usage. Describes the whole month, not the current page.
        currency (BillingUsagePageCurrency):
        data (list[BillingUsageWindow]): Usage windows for the current page, ordered by time (ascending). Windows with
            no usage are omitted.
        has_more (bool): True when more time windows are available beyond the current page.
        next_page_token (None | str): Opaque cursor for the next page; pass it back as `page_token`. Null when
            `has_more` is false.
    """

    object_: BillingUsagePageObject
    organization_id: str
    billing_period: str
    earliest_window_start: datetime.datetime | None
    latest_window_end: datetime.datetime | None
    currency: BillingUsagePageCurrency
    data: list[BillingUsageWindow]
    has_more: bool
    next_page_token: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        object_ = self.object_.value

        organization_id = self.organization_id

        billing_period = self.billing_period

        earliest_window_start: None | str
        if isinstance(self.earliest_window_start, datetime.datetime):
            earliest_window_start = self.earliest_window_start.isoformat()
        else:
            earliest_window_start = self.earliest_window_start

        latest_window_end: None | str
        if isinstance(self.latest_window_end, datetime.datetime):
            latest_window_end = self.latest_window_end.isoformat()
        else:
            latest_window_end = self.latest_window_end

        currency = self.currency.value

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        has_more = self.has_more

        next_page_token: None | str
        next_page_token = self.next_page_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "organization_id": organization_id,
                "billing_period": billing_period,
                "earliest_window_start": earliest_window_start,
                "latest_window_end": latest_window_end,
                "currency": currency,
                "data": data,
                "has_more": has_more,
                "next_page_token": next_page_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.billing_usage_window import BillingUsageWindow

        d = dict(src_dict)
        object_ = BillingUsagePageObject(d.pop("object"))

        organization_id = d.pop("organization_id")

        billing_period = d.pop("billing_period")

        def _parse_earliest_window_start(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                earliest_window_start_type_0 = isoparse(data)

                return earliest_window_start_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        earliest_window_start = _parse_earliest_window_start(
            d.pop("earliest_window_start")
        )

        def _parse_latest_window_end(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                latest_window_end_type_0 = isoparse(data)

                return latest_window_end_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        latest_window_end = _parse_latest_window_end(d.pop("latest_window_end"))

        currency = BillingUsagePageCurrency(d.pop("currency"))

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = BillingUsageWindow.from_dict(data_item_data)

            data.append(data_item)

        has_more = d.pop("has_more")

        def _parse_next_page_token(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_page_token = _parse_next_page_token(d.pop("next_page_token"))

        billing_usage_page = cls(
            object_=object_,
            organization_id=organization_id,
            billing_period=billing_period,
            earliest_window_start=earliest_window_start,
            latest_window_end=latest_window_end,
            currency=currency,
            data=data,
            has_more=has_more,
            next_page_token=next_page_token,
        )

        billing_usage_page.additional_properties = d
        return billing_usage_page

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
