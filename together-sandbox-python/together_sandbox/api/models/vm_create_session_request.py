from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.vm_create_session_request_permission import (
    VMCreateSessionRequestPermission,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="VMCreateSessionRequest")


@_attrs_define
class VMCreateSessionRequest:
    """
    Attributes:
        permission (VMCreateSessionRequestPermission): Permission level for the session Example: write.
        session_id (str): Unique identifier for the session Example: my-session-1.
        git_access_token (str | Unset): GitHub token for the session
        git_user_email (str | Unset): Git user email to configure for this session
        git_user_name (str | Unset): Git user name to configure for this session
    """

    permission: VMCreateSessionRequestPermission
    session_id: str
    git_access_token: str | Unset = UNSET
    git_user_email: str | Unset = UNSET
    git_user_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        permission = self.permission.value

        session_id = self.session_id

        git_access_token = self.git_access_token

        git_user_email = self.git_user_email

        git_user_name = self.git_user_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "permission": permission,
                "session_id": session_id,
            }
        )
        if git_access_token is not UNSET:
            field_dict["git_access_token"] = git_access_token
        if git_user_email is not UNSET:
            field_dict["git_user_email"] = git_user_email
        if git_user_name is not UNSET:
            field_dict["git_user_name"] = git_user_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        permission = VMCreateSessionRequestPermission(d.pop("permission"))

        session_id = d.pop("session_id")

        git_access_token = d.pop("git_access_token", UNSET)

        git_user_email = d.pop("git_user_email", UNSET)

        git_user_name = d.pop("git_user_name", UNSET)

        vm_create_session_request = cls(
            permission=permission,
            session_id=session_id,
            git_access_token=git_access_token,
            git_user_email=git_user_email,
            git_user_name=git_user_name,
        )

        vm_create_session_request.additional_properties = d
        return vm_create_session_request

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
