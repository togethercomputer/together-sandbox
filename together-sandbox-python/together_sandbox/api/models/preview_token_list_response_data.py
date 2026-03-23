from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.preview_token import PreviewToken


T = TypeVar("T", bound="PreviewTokenListResponseData")


@_attrs_define
class PreviewTokenListResponseData:
    """
    Attributes:
        sandbox_id (str):
        tokens (list[PreviewToken]):
    """

    sandbox_id: str
    tokens: list[PreviewToken]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sandbox_id = self.sandbox_id

        tokens = []
        for tokens_item_data in self.tokens:
            tokens_item = tokens_item_data.to_dict()
            tokens.append(tokens_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sandbox_id": sandbox_id,
                "tokens": tokens,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preview_token import PreviewToken

        d = dict(src_dict)
        sandbox_id = d.pop("sandbox_id")

        tokens = []
        _tokens = d.pop("tokens")
        for tokens_item_data in _tokens:
            tokens_item = PreviewToken.from_dict(tokens_item_data)

            tokens.append(tokens_item)

        preview_token_list_response_data = cls(
            sandbox_id=sandbox_id,
            tokens=tokens,
        )

        preview_token_list_response_data.additional_properties = d
        return preview_token_list_response_data

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
