from typing import Any, Callable, NoReturn, Optional, Protocol, cast, runtime_checkable

from ..models.preview_host_list_response import PreviewHostListResponse
from ..models.preview_host_request import PreviewHostRequest
from ..models.preview_token_create_request import PreviewTokenCreateRequest
from ..models.preview_token_create_response import PreviewTokenCreateResponse
from ..models.preview_token_list_response import PreviewTokenListResponse
from ..models.preview_token_revoke_all_response import PreviewTokenRevokeAllResponse
from ..models.preview_token_update_request import PreviewTokenUpdateRequest
from ..models.preview_token_update_response import PreviewTokenUpdateResponse
from ..models.token_create_request import TokenCreateRequest
from ..models.token_create_response import TokenCreateResponse
from ..models.token_update_request import TokenUpdateRequest
from ..models.token_update_response import TokenUpdateResponse
from ..models.workspace_create_request import WorkspaceCreateRequest
from ..models.workspace_create_response import WorkspaceCreateResponse
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_bytes
from together_sandbox.core.utils import DataclassSerializer

from ..models.preview_host_list_response import PreviewHostListResponse
from ..models.preview_host_request import PreviewHostRequest
from ..models.preview_token_create_request import PreviewTokenCreateRequest
from ..models.preview_token_create_response import PreviewTokenCreateResponse
from ..models.preview_token_list_response import PreviewTokenListResponse
from ..models.preview_token_revoke_all_response import PreviewTokenRevokeAllResponse
from ..models.preview_token_update_request import PreviewTokenUpdateRequest
from ..models.preview_token_update_response import PreviewTokenUpdateResponse
from ..models.token_create_request import TokenCreateRequest
from ..models.token_create_response import TokenCreateResponse
from ..models.token_update_request import TokenUpdateRequest
from ..models.token_update_response import TokenUpdateResponse
from ..models.workspace_create_request import WorkspaceCreateRequest
from ..models.workspace_create_response import WorkspaceCreateResponse

@runtime_checkable
class DefaultClientProtocol(Protocol):
    """Protocol defining the interface of DefaultClient for dependency injection."""
    
    async def workspace_create(
    self,
    body: WorkspaceCreateRequest | None = None,
    ) -> WorkspaceCreateResponse: ...
    
    async def token_create(
    self,
    team_id: str,
    body: TokenCreateRequest | None = None,
    ) -> TokenCreateResponse: ...
    
    async def token_update(
    self,
    team_id: str,
    token_id: str,
    body: TokenUpdateRequest | None = None,
    ) -> TokenUpdateResponse: ...
    
    async def preview_token_revoke_all(
    self,
    id_: str,
    ) -> PreviewTokenRevokeAllResponse: ...
    
    async def preview_token_list(
    self,
    id_: str,
    ) -> PreviewTokenListResponse: ...
    
    async def preview_token_create(
    self,
    id_: str,
    body: PreviewTokenCreateRequest | None = None,
    ) -> PreviewTokenCreateResponse: ...
    
    async def preview_token_update(
    self,
    id_: str,
    token_id: str,
    body: PreviewTokenUpdateRequest | None = None,
    ) -> PreviewTokenUpdateResponse: ...
    
    async def preview_host_list(
    self,
    ) -> PreviewHostListResponse: ...
    
    async def preview_host_create(
    self,
    body: PreviewHostRequest | None = None,
    ) -> PreviewHostListResponse: ...
    
    async def preview_host_update(
    self,
    body: PreviewHostRequest | None = None,
    ) -> PreviewHostListResponse: ...
    


class DefaultClient(DefaultClientProtocol):
    """Client for default endpoints. Uses HttpTransport for all HTTP and header management."""
    
    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url
    
    async def workspace_create(
        self,
        body: WorkspaceCreateRequest | None = None,
    ) -> WorkspaceCreateResponse:
        """
        Create a Workspace
        
        Create a new, empty, workspace in the current organization
        
        Args:
            body (WorkspaceCreateRequest | None)
                                     : Workspace Create Request (json)
        
        Returns:
            WorkspaceCreateResponse: Workspace Create Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/org/workspace"
        
        json_body: WorkspaceCreateRequest | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), WorkspaceCreateResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def token_create(
        self,
        team_id: str,
        body: TokenCreateRequest | None = None,
    ) -> TokenCreateResponse:
        """
        Create an API Token
        
        Create a new API token for a workspace that is part of the current organization.
        
        Args:
            team_id (str)            : ID of the workspace to create the token in
            body (TokenCreateRequest | None)
                                     : Token Create Request (json)
        
        Returns:
            TokenCreateResponse: Token Create Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        team_id = DataclassSerializer.serialize(team_id)
        
        url = f"{self.base_url}/org/workspace/{team_id}/tokens"
        
        json_body: TokenCreateRequest | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), TokenCreateResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def token_update(
        self,
        team_id: str,
        token_id: str,
        body: TokenUpdateRequest | None = None,
    ) -> TokenUpdateResponse:
        """
        Update an API Token
        
        Update an API token for a workspace that is part of the current organization.
        
        Args:
            team_id (str)            : ID of the workspace the token belongs to
            token_id (str)           : ID of token to update
            body (TokenUpdateRequest | None)
                                     : Token Update Request (json)
        
        Returns:
            TokenUpdateResponse: Token Update Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        team_id = DataclassSerializer.serialize(team_id)
        token_id = DataclassSerializer.serialize(token_id)
        
        url = f"{self.base_url}/org/workspace/{team_id}/tokens/{token_id}"
        
        json_body: TokenUpdateRequest | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("PATCH", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), TokenUpdateResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def preview_token_revoke_all(
        self,
        id_: str,
    ) -> PreviewTokenRevokeAllResponse:
        """
        Revoke preview tokens
        
        Immediately expires all active preview tokens associated with this sandbox
        
        Args:
            id (str)                 : Shortid of the sandbox to revoke tokens for
        
        Returns:
            PreviewTokenRevokeAllResponse: RevokeAllPreviewTokensResponse
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/sandbox/{id_}/tokens"
        
        response = await self._transport.request(
            "DELETE", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), PreviewTokenRevokeAllResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def preview_token_list(
        self,
        id_: str,
    ) -> PreviewTokenListResponse:
        """
        List Preview Tokens
        
        List information about the preview tokens associated with the current sandbox
        
        Args:
            id (str)                 : Shortid of the sandbox to list the tokens for
        
        Returns:
            PreviewTokenListResponse: Token List Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/sandbox/{id_}/tokens"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), PreviewTokenListResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def preview_token_create(
        self,
        id_: str,
        body: PreviewTokenCreateRequest | None = None,
    ) -> PreviewTokenCreateResponse:
        """
        Create a Preview Token
        
        Create a new Preview token that allow access to a private sandbox
        
        Args:
            id (str)                 : Shortid of the sandbox to create the token for
            body (PreviewTokenCreateRequest | None)
                                     : Token Create Request (json)
        
        Returns:
            PreviewTokenCreateResponse: Token Create Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/sandbox/{id_}/tokens"
        
        json_body: PreviewTokenCreateRequest | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), PreviewTokenCreateResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def preview_token_update(
        self,
        id_: str,
        token_id: str,
        body: PreviewTokenUpdateRequest | None = None,
    ) -> PreviewTokenUpdateResponse:
        """
        Update a Preview Token
        
        Update a Preview token that allow access to a private sandbox
        
        Args:
            id (str)                 : Shortid of the sandbox to create the token for
            token_id (str)           : ID of the token to update. Does not accept the token
                                       itself.
            body (PreviewTokenUpdateRequest | None)
                                     : Token Update Request (json)
        
        Returns:
            PreviewTokenUpdateResponse: Token Update Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        token_id = DataclassSerializer.serialize(token_id)
        
        url = f"{self.base_url}/sandbox/{id_}/tokens/{token_id}"
        
        json_body: PreviewTokenUpdateRequest | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("PATCH", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), PreviewTokenUpdateResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def preview_host_list(
        self,
    ) -> PreviewHostListResponse:
        """
        List Preview Hosts
        
        List all trusted preview hosts for the current team
        
        Returns:
            PreviewHostListResponse: Preview Host List Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/workspace/preview_hosts"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), PreviewHostListResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def preview_host_create(
        self,
        body: PreviewHostRequest | None = None,
    ) -> PreviewHostListResponse:
        """
        Create Preview Hosts
        
        Add one or more trusted domains that are allowed to access sandbox previews for this
        workspace.
        
        Args:
            body (PreviewHostRequest | None)
                                     : Preview Host Create Request (json)
        
        Returns:
            PreviewHostListResponse: Preview Host List Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/workspace/preview_hosts"
        
        json_body: PreviewHostRequest | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), PreviewHostListResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def preview_host_update(
        self,
        body: PreviewHostRequest | None = None,
    ) -> PreviewHostListResponse:
        """
        Update Preview Hosts
        
        Replace the list of trusted domains that are allowed to access sandbox previews for this
        workspace.
        
        Args:
            body (PreviewHostRequest | None)
                                     : Preview Host Update Request (json)
        
        Returns:
            PreviewHostListResponse: Preview Host List Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/workspace/preview_hosts"
        
        json_body: PreviewHostRequest | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("PUT", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), PreviewHostListResponse)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover