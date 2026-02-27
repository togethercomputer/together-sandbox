from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ExecItem")


@_attrs_define
class ExecItem:
    """
    Attributes:
        id (str): Exec unique identifier
        command (str): Command being executed
        args (list[str]): Command line arguments
        status (str): Exec status (e.g., running, stopped, finished)
        pid (int): Process ID of the exec
        interactive (bool): Whether the exec is interactive
        pty (bool): Whether the exec is using a pty
        exit_code (int): Exit code of the process (only present when process has exited)
    """

    id: str
    command: str
    args: list[str]
    status: str
    pid: int
    interactive: bool
    pty: bool
    exit_code: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        command = self.command

        args = self.args

        status = self.status

        pid = self.pid

        interactive = self.interactive

        pty = self.pty

        exit_code = self.exit_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "command": command,
                "args": args,
                "status": status,
                "pid": pid,
                "interactive": interactive,
                "pty": pty,
                "exitCode": exit_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        command = d.pop("command")

        args = cast(list[str], d.pop("args"))

        status = d.pop("status")

        pid = d.pop("pid")

        interactive = d.pop("interactive")

        pty = d.pop("pty")

        exit_code = d.pop("exitCode")

        exec_item = cls(
            id=id,
            command=command,
            args=args,
            status=status,
            pid=pid,
            interactive=interactive,
            pty=pty,
            exit_code=exit_code,
        )

        exec_item.additional_properties = d
        return exec_item

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
