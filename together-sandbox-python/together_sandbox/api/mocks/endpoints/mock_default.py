from typing import TYPE_CHECKING

from ...models.preview_host_list_response import PreviewHostListResponse
from ...models.preview_host_request import PreviewHostRequest
from ...models.preview_token_create_request import PreviewTokenCreateRequest
from ...models.preview_token_create_response import PreviewTokenCreateResponse
from ...models.preview_token_list_response import PreviewTokenListResponse
from ...models.preview_token_revoke_all_response import PreviewTokenRevokeAllResponse
from ...models.preview_token_update_request import PreviewTokenUpdateRequest
from ...models.preview_token_update_response import PreviewTokenUpdateResponse
from ...models.token_create_request import TokenCreateRequest
from ...models.token_create_response import TokenCreateResponse
from ...models.token_update_request import TokenUpdateRequest
from ...models.token_update_response import TokenUpdateResponse
from ...models.workspace_create_request import WorkspaceCreateRequest
from ...models.workspace_create_response import WorkspaceCreateResponse

if TYPE_CHECKING:
    pass


class MockDefaultClient:
    """
    Mock implementation of DefaultClient for testing.

    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.

    Example:
        class TestDefaultClient(MockDefaultClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """

    async def workspace_create(
        self,
        body: WorkspaceCreateRequest | None = None,
    ) -> WorkspaceCreateResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.workspace_create() not implemented. Override this method in your test subclass."
        )

    async def token_create(
        self,
        team_id: str,
        body: TokenCreateRequest | None = None,
    ) -> TokenCreateResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.token_create() not implemented. Override this method in your test subclass."
        )

    async def token_update(
        self,
        team_id: str,
        token_id: str,
        body: TokenUpdateRequest | None = None,
    ) -> TokenUpdateResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.token_update() not implemented. Override this method in your test subclass."
        )

    async def preview_token_revoke_all(
        self,
        id_: str,
    ) -> PreviewTokenRevokeAllResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.preview_token_revoke_all() not implemented. Override this method in your test subclass."
        )

    async def preview_token_list(
        self,
        id_: str,
    ) -> PreviewTokenListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.preview_token_list() not implemented. Override this method in your test subclass."
        )

    async def preview_token_create(
        self,
        id_: str,
        body: PreviewTokenCreateRequest | None = None,
    ) -> PreviewTokenCreateResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.preview_token_create() not implemented. Override this method in your test subclass."
        )

    async def preview_token_update(
        self,
        id_: str,
        token_id: str,
        body: PreviewTokenUpdateRequest | None = None,
    ) -> PreviewTokenUpdateResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.preview_token_update() not implemented. Override this method in your test subclass."
        )

    async def preview_host_list(
        self,
    ) -> PreviewHostListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.preview_host_list() not implemented. Override this method in your test subclass."
        )

    async def preview_host_create(
        self,
        body: PreviewHostRequest | None = None,
    ) -> PreviewHostListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.preview_host_create() not implemented. Override this method in your test subclass."
        )

    async def preview_host_update(
        self,
        body: PreviewHostRequest | None = None,
    ) -> PreviewHostListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockClient_Client.preview_host_update() not implemented. Override this method in your test subclass."
        )
