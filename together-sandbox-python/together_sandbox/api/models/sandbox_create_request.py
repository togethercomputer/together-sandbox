from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sandbox_create_request_runtime import SandboxCreateRequestRuntime
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sandbox_create_request_files import SandboxCreateRequestFiles
    from ..models.sandbox_create_request_npm_dependencies import SandboxCreateRequestNpmDependencies
    from ..models.sandbox_create_request_settings import SandboxCreateRequestSettings


T = TypeVar("T", bound="SandboxCreateRequest")


@_attrs_define
class SandboxCreateRequest:
    """
    Attributes:
        files (SandboxCreateRequestFiles): Map of `path => file` where each file is a map.
        description (str | Unset): Optional text description of the sandbox. Defaults to no description.
        entry (str | Unset): Filename of the entrypoint of the sandbox.
        external_resources (list[str] | Unset): Array of strings with external resources to load.
        is_frozen (bool | Unset): Whether changes to the sandbox are disallowed. Defaults to `false`. Default: False.
        npm_dependencies (SandboxCreateRequestNpmDependencies | Unset): Map of dependencies and their version
            specifications.
        path (str | Unset): Path to the collection where the new sandbox should be stored. Defaults to "/". If no
            collection exists at the given path, it will be created. Default: '/'.
        privacy (int | Unset): 0 for public, 1 for unlisted, and 2 for private. Privacy is subject to certain
            restrictions (team minimum setting, drafts must be private, etc.). Defaults to public. Default: 0.
        private_preview (bool | Unset): Determines whether the preview of a private sandbox is private or public. Has no
            effect on public or unlisted sandboxes; their previews are always publicly accessible
        runtime (SandboxCreateRequestRuntime | Unset): Runtime to use for the sandbox. Defaults to `"browser"`. Default:
            SandboxCreateRequestRuntime.BROWSER.
        settings (SandboxCreateRequestSettings | Unset): Sandbox settings.
        tags (list[str] | Unset): List of string tags to apply to the sandbox. Only the first ten will be used. Defaults
            to no tags.
        template (str | Unset): Name of the template from which the sandbox is derived (for example, `"static"`).
        title (str | Unset): Sandbox title. Maximum 255 characters. Defaults to no title. Default: ''.
    """

    files: SandboxCreateRequestFiles
    description: str | Unset = UNSET
    entry: str | Unset = UNSET
    external_resources: list[str] | Unset = UNSET
    is_frozen: bool | Unset = False
    npm_dependencies: SandboxCreateRequestNpmDependencies | Unset = UNSET
    path: str | Unset = "/"
    privacy: int | Unset = 0
    private_preview: bool | Unset = UNSET
    runtime: SandboxCreateRequestRuntime | Unset = SandboxCreateRequestRuntime.BROWSER
    settings: SandboxCreateRequestSettings | Unset = UNSET
    tags: list[str] | Unset = UNSET
    template: str | Unset = UNSET
    title: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = self.files.to_dict()

        description = self.description

        entry = self.entry

        external_resources: list[str] | Unset = UNSET
        if not isinstance(self.external_resources, Unset):
            external_resources = self.external_resources

        is_frozen = self.is_frozen

        npm_dependencies: dict[str, Any] | Unset = UNSET
        if not isinstance(self.npm_dependencies, Unset):
            npm_dependencies = self.npm_dependencies.to_dict()

        path = self.path

        privacy = self.privacy

        private_preview = self.private_preview

        runtime: str | Unset = UNSET
        if not isinstance(self.runtime, Unset):
            runtime = self.runtime.value

        settings: dict[str, Any] | Unset = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        template = self.template

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if entry is not UNSET:
            field_dict["entry"] = entry
        if external_resources is not UNSET:
            field_dict["external_resources"] = external_resources
        if is_frozen is not UNSET:
            field_dict["is_frozen"] = is_frozen
        if npm_dependencies is not UNSET:
            field_dict["npm_dependencies"] = npm_dependencies
        if path is not UNSET:
            field_dict["path"] = path
        if privacy is not UNSET:
            field_dict["privacy"] = privacy
        if private_preview is not UNSET:
            field_dict["private_preview"] = private_preview
        if runtime is not UNSET:
            field_dict["runtime"] = runtime
        if settings is not UNSET:
            field_dict["settings"] = settings
        if tags is not UNSET:
            field_dict["tags"] = tags
        if template is not UNSET:
            field_dict["template"] = template
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sandbox_create_request_files import SandboxCreateRequestFiles
        from ..models.sandbox_create_request_npm_dependencies import SandboxCreateRequestNpmDependencies
        from ..models.sandbox_create_request_settings import SandboxCreateRequestSettings

        d = dict(src_dict)
        files = SandboxCreateRequestFiles.from_dict(d.pop("files"))

        description = d.pop("description", UNSET)

        entry = d.pop("entry", UNSET)

        external_resources = cast(list[str], d.pop("external_resources", UNSET))

        is_frozen = d.pop("is_frozen", UNSET)

        _npm_dependencies = d.pop("npm_dependencies", UNSET)
        npm_dependencies: SandboxCreateRequestNpmDependencies | Unset
        if isinstance(_npm_dependencies, Unset):
            npm_dependencies = UNSET
        else:
            npm_dependencies = SandboxCreateRequestNpmDependencies.from_dict(_npm_dependencies)

        path = d.pop("path", UNSET)

        privacy = d.pop("privacy", UNSET)

        private_preview = d.pop("private_preview", UNSET)

        _runtime = d.pop("runtime", UNSET)
        runtime: SandboxCreateRequestRuntime | Unset
        if isinstance(_runtime, Unset):
            runtime = UNSET
        else:
            runtime = SandboxCreateRequestRuntime(_runtime)

        _settings = d.pop("settings", UNSET)
        settings: SandboxCreateRequestSettings | Unset
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = SandboxCreateRequestSettings.from_dict(_settings)

        tags = cast(list[str], d.pop("tags", UNSET))

        template = d.pop("template", UNSET)

        title = d.pop("title", UNSET)

        sandbox_create_request = cls(
            files=files,
            description=description,
            entry=entry,
            external_resources=external_resources,
            is_frozen=is_frozen,
            npm_dependencies=npm_dependencies,
            path=path,
            privacy=privacy,
            private_preview=private_preview,
            runtime=runtime,
            settings=settings,
            tags=tags,
            template=template,
            title=title,
        )

        sandbox_create_request.additional_properties = d
        return sandbox_create_request

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
