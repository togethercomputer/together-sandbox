from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.error_type import ErrorType

if TYPE_CHECKING:
    from ..models.error_errors_item import ErrorErrorsItem


T = TypeVar("T", bound="Error")


@_attrs_define
class Error:
    """
    Attributes:
        field_type_ (ErrorType):
        code (str):
        message (str):
        errors (list[ErrorErrorsItem]):
    """

    field_type_: ErrorType
    code: str
    message: str
    errors: list[ErrorErrorsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_type_ = self.field_type_.value

        code = self.code

        message = self.message

        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_type": field_type_,
                "code": code,
                "message": message,
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_errors_item import ErrorErrorsItem

        d = dict(src_dict)
        field_type_ = ErrorType(d.pop("_type"))

        code = d.pop("code")

        message = d.pop("message")

        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = ErrorErrorsItem.from_dict(errors_item_data)

            errors.append(errors_item)

        error = cls(
            field_type_=field_type_,
            code=code,
            message=message,
            errors=errors,
        )

        error.additional_properties = d
        return error

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
