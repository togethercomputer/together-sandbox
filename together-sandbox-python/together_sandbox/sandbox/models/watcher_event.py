from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.watcher_event_type import WatcherEventType

T = TypeVar("T", bound="WatcherEvent")


@_attrs_define
class WatcherEvent:
    """
    Attributes:
        paths (list[str]): File paths affected by the event
        type_ (WatcherEventType): Type of file system event
        timestamp (datetime.datetime): Timestamp of when the event occurred
    """

    paths: list[str]
    type_: WatcherEventType
    timestamp: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        paths = self.paths

        type_ = self.type_.value

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paths": paths,
                "type": type_,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        paths = cast(list[str], d.pop("paths"))

        type_ = WatcherEventType(d.pop("type"))

        timestamp = isoparse(d.pop("timestamp"))

        watcher_event = cls(
            paths=paths,
            type_=type_,
            timestamp=timestamp,
        )

        watcher_event.additional_properties = d
        return watcher_event

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
