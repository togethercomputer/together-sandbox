from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.setup_task_item import SetupTaskItem


T = TypeVar("T", bound="SetupTaskListResponse")


@_attrs_define
class SetupTaskListResponse:
    """
    Attributes:
        setup_tasks (list[SetupTaskItem]):
    """

    setup_tasks: list[SetupTaskItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        setup_tasks = []
        for setup_tasks_item_data in self.setup_tasks:
            setup_tasks_item = setup_tasks_item_data.to_dict()
            setup_tasks.append(setup_tasks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "setupTasks": setup_tasks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.setup_task_item import SetupTaskItem

        d = dict(src_dict)
        setup_tasks = []
        _setup_tasks = d.pop("setupTasks")
        for setup_tasks_item_data in _setup_tasks:
            setup_tasks_item = SetupTaskItem.from_dict(setup_tasks_item_data)

            setup_tasks.append(setup_tasks_item)

        setup_task_list_response = cls(
            setup_tasks=setup_tasks,
        )

        setup_task_list_response.additional_properties = d
        return setup_task_list_response

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
