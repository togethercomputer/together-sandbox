from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.response_errors_item_type_1 import ResponseErrorsItemType1


T = TypeVar("T", bound="Response")


@_attrs_define
class Response:
    """
    Attributes:
        errors (list[ResponseErrorsItemType1 | str] | Unset):
        success (bool | Unset):
    """

    errors: list[ResponseErrorsItemType1 | str] | Unset = UNSET
    success: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.response_errors_item_type_1 import ResponseErrorsItemType1

        errors: list[dict[str, Any] | str] | Unset = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item: dict[str, Any] | str
                if isinstance(errors_item_data, ResponseErrorsItemType1):
                    errors_item = errors_item_data.to_dict()
                else:
                    errors_item = errors_item_data
                errors.append(errors_item)

        success = self.success

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if errors is not UNSET:
            field_dict["errors"] = errors
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.response_errors_item_type_1 import ResponseErrorsItemType1

        d = dict(src_dict)
        _errors = d.pop("errors", UNSET)
        errors: list[ResponseErrorsItemType1 | str] | Unset = UNSET
        if _errors is not UNSET:
            errors = []
            for errors_item_data in _errors:

                def _parse_errors_item(data: object) -> ResponseErrorsItemType1 | str:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        errors_item_type_1 = ResponseErrorsItemType1.from_dict(data)

                        return errors_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    return cast(ResponseErrorsItemType1 | str, data)

                errors_item = _parse_errors_item(errors_item_data)

                errors.append(errors_item)

        success = d.pop("success", UNSET)

        response = cls(
            errors=errors,
            success=success,
        )

        response.additional_properties = d
        return response

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
