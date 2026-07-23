from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.task_status import TaskStatus

T = TypeVar("T", bound="TaskActionResponse")


@_attrs_define
class TaskActionResponse:
    """Schema for task action responses, containing details about the task and the action performed.

    Attributes:
        status (TaskStatus):
        exec_id (str): Exec identifier associated with the task
        start_time (str): Task start time in RFC3339 format Example: 2017-07-21T17:32:28Z.
        end_time (str): Task end time in RFC3339 format Example: 2017-08-21T17:32:28Z.
        id (str): Task identifier
        name (str): Task name
        command (str): Task command
        message (str): Action result message
    """

    status: TaskStatus
    exec_id: str
    start_time: str
    end_time: str
    id: str
    name: str
    command: str
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        exec_id = self.exec_id

        start_time = self.start_time

        end_time = self.end_time

        id = self.id

        name = self.name

        command = self.command

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "execId": exec_id,
                "startTime": start_time,
                "endTime": end_time,
                "id": id,
                "name": name,
                "command": command,
                "message": message,
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

        id = d.pop("id")

        name = d.pop("name")

        command = d.pop("command")

        message = d.pop("message")

        task_action_response = cls(
            status=status,
            exec_id=exec_id,
            start_time=start_time,
            end_time=end_time,
            id=id,
            name=name,
            command=command,
            message=message,
        )

        task_action_response.additional_properties = d
        return task_action_response

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
