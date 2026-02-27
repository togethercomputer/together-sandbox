from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sandbox_fork_response_data_start_response_type_0 import SandboxForkResponseDataStartResponseType0


T = TypeVar("T", bound="SandboxForkResponseData")


@_attrs_define
class SandboxForkResponseData:
    """
    Attributes:
        alias (str):
        id (str):
        title (None | str):
        start_response (None | SandboxForkResponseDataStartResponseType0 | Unset): VM start response. Only present when
            start_options were provided in the request.
    """

    alias: str
    id: str
    title: None | str
    start_response: None | SandboxForkResponseDataStartResponseType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sandbox_fork_response_data_start_response_type_0 import SandboxForkResponseDataStartResponseType0

        alias = self.alias

        id = self.id

        title: None | str
        title = self.title

        start_response: dict[str, Any] | None | Unset
        if isinstance(self.start_response, Unset):
            start_response = UNSET
        elif isinstance(self.start_response, SandboxForkResponseDataStartResponseType0):
            start_response = self.start_response.to_dict()
        else:
            start_response = self.start_response

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "alias": alias,
                "id": id,
                "title": title,
            }
        )
        if start_response is not UNSET:
            field_dict["start_response"] = start_response

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sandbox_fork_response_data_start_response_type_0 import SandboxForkResponseDataStartResponseType0

        d = dict(src_dict)
        alias = d.pop("alias")

        id = d.pop("id")

        def _parse_title(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        title = _parse_title(d.pop("title"))

        def _parse_start_response(data: object) -> None | SandboxForkResponseDataStartResponseType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                start_response_type_0 = SandboxForkResponseDataStartResponseType0.from_dict(data)

                return start_response_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SandboxForkResponseDataStartResponseType0 | Unset, data)

        start_response = _parse_start_response(d.pop("start_response", UNSET))

        sandbox_fork_response_data = cls(
            alias=alias,
            id=id,
            title=title,
            start_response=start_response,
        )

        sandbox_fork_response_data.additional_properties = d
        return sandbox_fork_response_data

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
