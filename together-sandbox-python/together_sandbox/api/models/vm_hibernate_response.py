from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.vm_hibernate_response_data import VMHibernateResponseData
    from ..models.vm_hibernate_response_errors_item_type_1 import VMHibernateResponseErrorsItemType1


T = TypeVar("T", bound="VMHibernateResponse")


@_attrs_define
class VMHibernateResponse:
    """
    Attributes:
        errors (list[str | VMHibernateResponseErrorsItemType1] | Unset):
        success (bool | Unset):
        data (VMHibernateResponseData | Unset):
    """

    errors: list[str | VMHibernateResponseErrorsItemType1] | Unset = UNSET
    success: bool | Unset = UNSET
    data: VMHibernateResponseData | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.vm_hibernate_response_errors_item_type_1 import VMHibernateResponseErrorsItemType1

        errors: list[dict[str, Any] | str] | Unset = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item: dict[str, Any] | str
                if isinstance(errors_item_data, VMHibernateResponseErrorsItemType1):
                    errors_item = errors_item_data.to_dict()
                else:
                    errors_item = errors_item_data
                errors.append(errors_item)

        success = self.success

        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if errors is not UNSET:
            field_dict["errors"] = errors
        if success is not UNSET:
            field_dict["success"] = success
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vm_hibernate_response_data import VMHibernateResponseData
        from ..models.vm_hibernate_response_errors_item_type_1 import VMHibernateResponseErrorsItemType1

        d = dict(src_dict)
        _errors = d.pop("errors", UNSET)
        errors: list[str | VMHibernateResponseErrorsItemType1] | Unset = UNSET
        if _errors is not UNSET:
            errors = []
            for errors_item_data in _errors:

                def _parse_errors_item(data: object) -> str | VMHibernateResponseErrorsItemType1:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        errors_item_type_1 = VMHibernateResponseErrorsItemType1.from_dict(data)

                        return errors_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    return cast(str | VMHibernateResponseErrorsItemType1, data)

                errors_item = _parse_errors_item(errors_item_data)

                errors.append(errors_item)

        success = d.pop("success", UNSET)

        _data = d.pop("data", UNSET)
        data: VMHibernateResponseData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = VMHibernateResponseData.from_dict(_data)

        vm_hibernate_response = cls(
            errors=errors,
            success=success,
            data=data,
        )

        vm_hibernate_response.additional_properties = d
        return vm_hibernate_response

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
