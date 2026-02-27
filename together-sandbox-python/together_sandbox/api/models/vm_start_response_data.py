from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VMStartResponseData")


@_attrs_define
class VMStartResponseData:
    """
    Attributes:
        bootup_type (str):
        cluster (str):
        id (str):
        latest_pitcher_version (str):
        pitcher_manager_version (str):
        pitcher_token (str):
        pitcher_url (str):
        pitcher_version (str):
        reconnect_token (str):
        use_pint (bool):
        user_workspace_path (str):
        vm_agent_type (str):
        workspace_path (str):
        pint_token (str | Unset):
        pint_url (str | Unset):
    """

    bootup_type: str
    cluster: str
    id: str
    latest_pitcher_version: str
    pitcher_manager_version: str
    pitcher_token: str
    pitcher_url: str
    pitcher_version: str
    reconnect_token: str
    use_pint: bool
    user_workspace_path: str
    vm_agent_type: str
    workspace_path: str
    pint_token: str | Unset = UNSET
    pint_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bootup_type = self.bootup_type

        cluster = self.cluster

        id = self.id

        latest_pitcher_version = self.latest_pitcher_version

        pitcher_manager_version = self.pitcher_manager_version

        pitcher_token = self.pitcher_token

        pitcher_url = self.pitcher_url

        pitcher_version = self.pitcher_version

        reconnect_token = self.reconnect_token

        use_pint = self.use_pint

        user_workspace_path = self.user_workspace_path

        vm_agent_type = self.vm_agent_type

        workspace_path = self.workspace_path

        pint_token = self.pint_token

        pint_url = self.pint_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bootup_type": bootup_type,
                "cluster": cluster,
                "id": id,
                "latest_pitcher_version": latest_pitcher_version,
                "pitcher_manager_version": pitcher_manager_version,
                "pitcher_token": pitcher_token,
                "pitcher_url": pitcher_url,
                "pitcher_version": pitcher_version,
                "reconnect_token": reconnect_token,
                "use_pint": use_pint,
                "user_workspace_path": user_workspace_path,
                "vm_agent_type": vm_agent_type,
                "workspace_path": workspace_path,
            }
        )
        if pint_token is not UNSET:
            field_dict["pint_token"] = pint_token
        if pint_url is not UNSET:
            field_dict["pint_url"] = pint_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bootup_type = d.pop("bootup_type")

        cluster = d.pop("cluster")

        id = d.pop("id")

        latest_pitcher_version = d.pop("latest_pitcher_version")

        pitcher_manager_version = d.pop("pitcher_manager_version")

        pitcher_token = d.pop("pitcher_token")

        pitcher_url = d.pop("pitcher_url")

        pitcher_version = d.pop("pitcher_version")

        reconnect_token = d.pop("reconnect_token")

        use_pint = d.pop("use_pint")

        user_workspace_path = d.pop("user_workspace_path")

        vm_agent_type = d.pop("vm_agent_type")

        workspace_path = d.pop("workspace_path")

        pint_token = d.pop("pint_token", UNSET)

        pint_url = d.pop("pint_url", UNSET)

        vm_start_response_data = cls(
            bootup_type=bootup_type,
            cluster=cluster,
            id=id,
            latest_pitcher_version=latest_pitcher_version,
            pitcher_manager_version=pitcher_manager_version,
            pitcher_token=pitcher_token,
            pitcher_url=pitcher_url,
            pitcher_version=pitcher_version,
            reconnect_token=reconnect_token,
            use_pint=use_pint,
            user_workspace_path=user_workspace_path,
            vm_agent_type=vm_agent_type,
            workspace_path=workspace_path,
            pint_token=pint_token,
            pint_url=pint_url,
        )

        vm_start_response_data.additional_properties = d
        return vm_start_response_data

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
