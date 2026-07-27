from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.exec_stdout_type import ExecStdoutType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ExecStdout")


@_attrs_define
class ExecStdout:
    """
    Attributes:
        type_ (ExecStdoutType): Type of the exec output
        output (str): Data associated with the exec output
        sequence (int): Sequence number of the output message
        timestamp (datetime.datetime | Unset): Timestamp of when the output was generated
        exit_code (int | Unset): Exit code of the process (only present when process has exited)
    """

    type_: ExecStdoutType
    output: str
    sequence: int
    timestamp: datetime.datetime | Unset = UNSET
    exit_code: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        output = self.output

        sequence = self.sequence

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        exit_code = self.exit_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "output": output,
                "sequence": sequence,
            }
        )
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if exit_code is not UNSET:
            field_dict["exitCode"] = exit_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = ExecStdoutType(d.pop("type"))

        output = d.pop("output")

        sequence = d.pop("sequence")

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        exit_code = d.pop("exitCode", UNSET)

        exec_stdout = cls(
            type_=type_,
            output=output,
            sequence=sequence,
            timestamp=timestamp,
            exit_code=exit_code,
        )

        exec_stdout.additional_properties = d
        return exec_stdout

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
