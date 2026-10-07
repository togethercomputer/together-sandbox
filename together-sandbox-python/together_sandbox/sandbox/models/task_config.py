from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.task_preview import TaskPreview
    from ..models.task_restart import TaskRestart


T = TypeVar("T", bound="TaskConfig")


@_attrs_define
class TaskConfig:
    """
    Attributes:
        name (str):
        command (str):
        run_at_start (bool):
        restart_on (TaskRestart):
        preview (TaskPreview):
    """

    name: str
    command: str
    run_at_start: bool
    restart_on: TaskRestart
    preview: TaskPreview
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        command = self.command

        run_at_start = self.run_at_start

        restart_on = self.restart_on.to_dict()

        preview = self.preview.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "command": command,
                "runAtStart": run_at_start,
                "restartOn": restart_on,
                "preview": preview,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_preview import TaskPreview
        from ..models.task_restart import TaskRestart

        d = dict(src_dict)
        name = d.pop("name")

        command = d.pop("command")

        run_at_start = d.pop("runAtStart")

        restart_on = TaskRestart.from_dict(d.pop("restartOn"))

        preview = TaskPreview.from_dict(d.pop("preview"))

        task_config = cls(
            name=name,
            command=command,
            run_at_start=run_at_start,
            restart_on=restart_on,
            preview=preview,
        )

        task_config.additional_properties = d
        return task_config

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
