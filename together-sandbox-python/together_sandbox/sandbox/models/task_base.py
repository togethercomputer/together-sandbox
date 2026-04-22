from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.task_status import TaskStatus

T = TypeVar("T", bound="TaskBase")


@_attrs_define
class TaskBase:
    """Base schema for a task item, containing common fields shared across different task types.

    Attributes:
        status (TaskStatus):
        exec_id (str): Exec identifier associated with the task
        start_time (str): Task start time in RFC3339 format Example: 2017-07-21T17:32:28Z.
        end_time (str): Task end time in RFC3339 format Example: 2017-08-21T17:32:28Z.
    """

    status: TaskStatus
    exec_id: str
    start_time: str
    end_time: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        exec_id = self.exec_id

        start_time = self.start_time

        end_time = self.end_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "execId": exec_id,
                "startTime": start_time,
                "endTime": end_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = TaskStatus(d.pop("status"))

        exec_id = d.pop("execId")

        start_time = d.pop("startTime")

        end_time = d.pop("endTime")

        task_base = cls(
            status=status,
            exec_id=exec_id,
            start_time=start_time,
            end_time=end_time,
        )

        task_base.additional_properties = d
        return task_base

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
