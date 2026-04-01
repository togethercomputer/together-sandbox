from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sandbox_fork_request_start_options import (
        SandboxForkRequestStartOptions,
    )


T = TypeVar("T", bound="SandboxForkRequest")


@_attrs_define
class SandboxForkRequest:
    """
    Attributes:
        description (str | Unset): Sandbox description. Maximum 255 characters. Defaults to description of original
            sandbox. Default: '[Original description]'.
        is_frozen (bool | Unset): Sandbox frozen status. When true, edits to the sandbox are restricted. Defaults to
            frozen status of the original sandbox. Default: False.
        path (str | Unset): Path to the collection where the new sandbox should be stored. Defaults to "/". If no
            collection exists at the given path, it will be created. Default: '/'.
        privacy (int | Unset): Sandbox privacy. 0 for public, 1 for unlisted, and 2 for private. Subject to the minimum
            privacy restrictions of the workspace. Defaults to the privacy of the original sandbox. Default: 0.
        private_preview (bool | Unset): Determines whether the preview of a private sandbox is private or public. Has no
            effect on public or unlisted sandboxes; their previews are always publicly accessible
        start_options (SandboxForkRequestStartOptions | Unset): Optional VM start configuration. If provided, the
            sandbox VM will be started immediately after creation.
        tags (list[str] | Unset): Tags to set on the new sandbox, if any. Will not inherit tags from the source sandbox.
        title (str | Unset): Sandbox title. Maximum 255 characters. Defaults to title of original sandbox with (forked).
            Default: '[Original title]'.
    """

    description: str | Unset = "[Original description]"
    is_frozen: bool | Unset = False
    path: str | Unset = "/"
    privacy: int | Unset = 0
    private_preview: bool | Unset = UNSET
    start_options: SandboxForkRequestStartOptions | Unset = UNSET
    tags: list[str] | Unset = UNSET
    title: str | Unset = "[Original title]"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        is_frozen = self.is_frozen

        path = self.path

        privacy = self.privacy

        private_preview = self.private_preview

        start_options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.start_options, Unset):
            start_options = self.start_options.to_dict()

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if is_frozen is not UNSET:
            field_dict["is_frozen"] = is_frozen
        if path is not UNSET:
            field_dict["path"] = path
        if privacy is not UNSET:
            field_dict["privacy"] = privacy
        if private_preview is not UNSET:
            field_dict["private_preview"] = private_preview
        if start_options is not UNSET:
            field_dict["start_options"] = start_options
        if tags is not UNSET:
            field_dict["tags"] = tags
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sandbox_fork_request_start_options import (
            SandboxForkRequestStartOptions,
        )

        d = dict(src_dict)
        description = d.pop("description", UNSET)

        is_frozen = d.pop("is_frozen", UNSET)

        path = d.pop("path", UNSET)

        privacy = d.pop("privacy", UNSET)

        private_preview = d.pop("private_preview", UNSET)

        _start_options = d.pop("start_options", UNSET)
        start_options: SandboxForkRequestStartOptions | Unset
        if isinstance(_start_options, Unset):
            start_options = UNSET
        else:
            start_options = SandboxForkRequestStartOptions.from_dict(_start_options)

        tags = cast(list[str], d.pop("tags", UNSET))

        title = d.pop("title", UNSET)

        sandbox_fork_request = cls(
            description=description,
            is_frozen=is_frozen,
            path=path,
            privacy=privacy,
            private_preview=private_preview,
            start_options=start_options,
            tags=tags,
            title=title,
        )

        sandbox_fork_request.additional_properties = d
        return sandbox_fork_request

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
