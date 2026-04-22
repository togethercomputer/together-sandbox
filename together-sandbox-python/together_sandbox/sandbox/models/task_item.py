from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.task_status import TaskStatus

if TYPE_CHECKING:
    from ..models.task_config import TaskConfig


T = TypeVar("T", bound="TaskItem")


@_attrs_define
class TaskItem:
    """
    Attributes:
        status (TaskStatus):
        exec_id (str): Exec identifier associated with the task
        start_time (str): Task start time in RFC3339 format Example: 2017-07-21T17:32:28Z.
        end_time (str): Task end time in RFC3339 format Example: 2017-08-21T17:32:28Z.
        id (str): Task identifier
        config (TaskConfig):
    """

    status: TaskStatus
    exec_id: str
    start_time: str
    end_time: str
    id: str
    config: TaskConfig
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        exec_id = self.exec_id

        start_time = self.start_time

        end_time = self.end_time

        id = self.id

        config = self.config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "execId": exec_id,
                "startTime": start_time,
                "endTime": end_time,
                "id": id,
                "config": config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_config import TaskConfig

        d = dict(src_dict)
        status = TaskStatus(d.pop("status"))

        exec_id = d.pop("execId")

        start_time = d.pop("startTime")

        end_time = d.pop("endTime")

        id = d.pop("id")

        config = TaskConfig.from_dict(d.pop("config"))

        task_item = cls(
            status=status,
            exec_id=exec_id,
            start_time=start_time,
            end_time=end_time,
            id=id,
            config=config,
        )

        task_item.additional_properties = d
        return task_item

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
