from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_exec_request_env import CreateExecRequestEnv


T = TypeVar("T", bound="CreateExecRequest")


@_attrs_define
class CreateExecRequest:
    """
    Attributes:
        command (str): Command to execute in the exec
        args (list[str]): Command line arguments
        autorun (bool | Unset): Whether to automatically start the exec (defaults to true)
        interactive (bool | Unset): Whether to start interactive shell session or not (defaults to false)
        pty (bool | Unset): Whether to start pty shell session or not (defaults to false)
        cwd (str | Unset): Working directory for the command (defaults to workspace directory if not specified)
        env (CreateExecRequestEnv | Unset): Environment variables to set for the command (key-value pairs)
    """

    command: str
    args: list[str]
    autorun: bool | Unset = UNSET
    interactive: bool | Unset = UNSET
    pty: bool | Unset = UNSET
    cwd: str | Unset = UNSET
    env: CreateExecRequestEnv | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        command = self.command

        args = self.args

        autorun = self.autorun

        interactive = self.interactive

        pty = self.pty

        cwd = self.cwd

        env: dict[str, Any] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = self.env.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "command": command,
                "args": args,
            }
        )
        if autorun is not UNSET:
            field_dict["autorun"] = autorun
        if interactive is not UNSET:
            field_dict["interactive"] = interactive
        if pty is not UNSET:
            field_dict["pty"] = pty
        if cwd is not UNSET:
            field_dict["cwd"] = cwd
        if env is not UNSET:
            field_dict["env"] = env

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_exec_request_env import CreateExecRequestEnv

        d = dict(src_dict)
        command = d.pop("command")

        args = cast(list[str], d.pop("args"))

        autorun = d.pop("autorun", UNSET)

        interactive = d.pop("interactive", UNSET)

        pty = d.pop("pty", UNSET)

        cwd = d.pop("cwd", UNSET)

        _env = d.pop("env", UNSET)
        env: CreateExecRequestEnv | Unset
        if isinstance(_env, Unset):
            env = UNSET
        else:
            env = CreateExecRequestEnv.from_dict(_env)

        create_exec_request = cls(
            command=command,
            args=args,
            autorun=autorun,
            interactive=interactive,
            pty=pty,
            cwd=cwd,
            env=env,
        )

        create_exec_request.additional_properties = d
        return create_exec_request

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
