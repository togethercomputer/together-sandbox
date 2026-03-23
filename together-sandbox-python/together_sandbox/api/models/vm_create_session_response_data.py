from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vm_create_session_response_data_permissions import (
        VMCreateSessionResponseDataPermissions,
    )


T = TypeVar("T", bound="VMCreateSessionResponseData")


@_attrs_define
class VMCreateSessionResponseData:
    """
    Attributes:
        capabilities (list[str]): List of capabilities that Pitcher has
        permissions (VMCreateSessionResponseDataPermissions): The permissions of the current session
        pitcher_token (str): Token to authenticate with Pitcher (the agent running inside the VM)
        pitcher_url (str): WebSocket URL to connect to Pitcher
        user_workspace_path (str): Path to the user's workspace in the VM
        username (str): The Linux username created for this session
    """

    capabilities: list[str]
    permissions: VMCreateSessionResponseDataPermissions
    pitcher_token: str
    pitcher_url: str
    user_workspace_path: str
    username: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        capabilities = self.capabilities

        permissions = self.permissions.to_dict()

        pitcher_token = self.pitcher_token

        pitcher_url = self.pitcher_url

        user_workspace_path = self.user_workspace_path

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "capabilities": capabilities,
                "permissions": permissions,
                "pitcher_token": pitcher_token,
                "pitcher_url": pitcher_url,
                "user_workspace_path": user_workspace_path,
                "username": username,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vm_create_session_response_data_permissions import (
            VMCreateSessionResponseDataPermissions,
        )

        d = dict(src_dict)
        capabilities = cast(list[str], d.pop("capabilities"))

        permissions = VMCreateSessionResponseDataPermissions.from_dict(
            d.pop("permissions")
        )

        pitcher_token = d.pop("pitcher_token")

        pitcher_url = d.pop("pitcher_url")

        user_workspace_path = d.pop("user_workspace_path")

        username = d.pop("username")

        vm_create_session_response_data = cls(
            capabilities=capabilities,
            permissions=permissions,
            pitcher_token=pitcher_token,
            pitcher_url=pitcher_url,
            user_workspace_path=user_workspace_path,
            username=username,
        )

        vm_create_session_response_data.additional_properties = d
        return vm_create_session_response_data

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
