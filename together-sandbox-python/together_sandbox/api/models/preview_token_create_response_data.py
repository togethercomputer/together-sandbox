from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.preview_token_create_response_data_token import (
        PreviewTokenCreateResponseDataToken,
    )


T = TypeVar("T", bound="PreviewTokenCreateResponseData")


@_attrs_define
class PreviewTokenCreateResponseData:
    """
    Attributes:
        sandbox_id (str):
        token (PreviewTokenCreateResponseDataToken):
    """

    sandbox_id: str
    token: PreviewTokenCreateResponseDataToken
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sandbox_id = self.sandbox_id

        token = self.token.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sandbox_id": sandbox_id,
                "token": token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preview_token_create_response_data_token import (
            PreviewTokenCreateResponseDataToken,
        )

        d = dict(src_dict)
        sandbox_id = d.pop("sandbox_id")

        token = PreviewTokenCreateResponseDataToken.from_dict(d.pop("token"))

        preview_token_create_response_data = cls(
            sandbox_id=sandbox_id,
            token=token,
        )

        preview_token_create_response_data.additional_properties = d
        return preview_token_create_response_data

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
