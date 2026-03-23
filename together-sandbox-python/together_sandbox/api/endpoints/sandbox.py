from typing import Any, Protocol, runtime_checkable

from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.utils import DataclassSerializer

from ..models.sandbox_create_request import SandboxCreateRequest
from ..models.sandbox_create_response import SandboxCreateResponse
from ..models.sandbox_fork_request import SandboxForkRequest
from ..models.sandbox_fork_response import SandboxForkResponse
from ..models.sandbox_get_response import SandboxGetResponse
from ..models.sandbox_list_response import SandboxListResponse


@runtime_checkable
class SandboxClientProtocol(Protocol):
    """Protocol defining the interface of SandboxClient for dependency injection."""

    async def sandbox_list(
        self,
        tags: str | None = None,
        order_by: str | None = None,
        direction: str | None = None,
        page_size: int | None = None,
        page: int | None = None,
        status: str | None = None,
    ) -> SandboxListResponse: ...

    async def sandbox_create(
        self,
        body: SandboxCreateRequest | None = None,
    ) -> SandboxCreateResponse: ...

    async def sandbox_get(
        self,
        id_: str,
    ) -> SandboxGetResponse: ...

    async def sandbox_fork(
        self,
        id_: str,
        body: SandboxForkRequest | None = None,
    ) -> SandboxForkResponse: ...


class SandboxClient(SandboxClientProtocol):
    """Client for sandbox endpoints. Uses HttpTransport for all HTTP and header management."""

    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url

    async def sandbox_list(
        self,
        tags: str | None = None,
        order_by: str | None = None,
        direction: str | None = None,
        page_size: int | None = None,
        page: int | None = None,
        status: str | None = None,
    ) -> SandboxListResponse:
        """
        List Sandboxes

        List sandboxes from the current workspace with optional filters. Results are limited to
        a maximum of 50 sandboxes per request.

        Args:
            tags (str | None)        : Comma-separated list of tags to filter by
            order_by (str | None)    : Field to order results by
            direction (str | None)   : Order direction
            page_size (int | None)   : Maximum number of sandboxes to return in a single
                                       response
            page (int | None)        : Page number to return
            status (str | None)      : If true, only returns VMs for which a heartbeat was
                                       received in the last 30 seconds.

        Returns:
            SandboxListResponse: Sandbox List Response

        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/sandbox"

        params: dict[str, Any] = {
            **(
                {"tags": DataclassSerializer.serialize(tags)}
                if tags is not None
                else {}
            ),
            **(
                {"order_by": DataclassSerializer.serialize(order_by)}
                if order_by is not None
                else {}
            ),
            **(
                {"direction": DataclassSerializer.serialize(direction)}
                if direction is not None
                else {}
            ),
            **(
                {"page_size": DataclassSerializer.serialize(page_size)}
                if page_size is not None
                else {}
            ),
            **(
                {"page": DataclassSerializer.serialize(page)}
                if page is not None
                else {}
            ),
            **(
                {"status": DataclassSerializer.serialize(status)}
                if status is not None
                else {}
            ),
        }

        response = await self._transport.request(
            "GET", url, params=params, json=None, data=None, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), SandboxListResponse)
            case _:
                raise HTTPError(
                    response=response,
                    message="Unhandled status code",
                    status_code=response.status_code,
                )
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def sandbox_create(
        self,
        body: SandboxCreateRequest | None = None,
    ) -> SandboxCreateResponse:
        """
        Create a Sandbox

        Create a new sandbox in the current workspace with file contents

        Args:
            body (SandboxCreateRequest | None)
                                     : Sandbox Create Request (json)

        Returns:
            SandboxCreateResponse: Sandbox Create Response

        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/sandbox"

        json_body: SandboxCreateRequest | None = DataclassSerializer.serialize(body)

        response = await self._transport.request(
            "POST", url, params=None, json=json_body, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), SandboxCreateResponse)
            case _:
                raise HTTPError(
                    response=response,
                    message="Unhandled status code",
                    status_code=response.status_code,
                )
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def sandbox_get(
        self,
        id_: str,
    ) -> SandboxGetResponse:
        """
        Get a Sandbox

        Retrieve a sandbox by its ID

        Args:
            id (str)                 : Short ID of the sandbox to retrieve

        Returns:
            SandboxGetResponse: Sandbox Get Response

        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)

        url = f"{self.base_url}/sandbox/{id_}"

        response = await self._transport.request(
            "GET", url, params=None, json=None, data=None, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), SandboxGetResponse)
            case _:
                raise HTTPError(
                    response=response,
                    message="Unhandled status code",
                    status_code=response.status_code,
                )
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def sandbox_fork(
        self,
        id_: str,
        body: SandboxForkRequest | None = None,
    ) -> SandboxForkResponse:
        """
        Fork a Sandbox

        Fork an existing sandbox to the current workspace

        Args:
            id (str)                 : Short ID of the sandbox to fork
            body (SandboxForkRequest | None)
                                     : Sandbox Fork Request (json)

        Returns:
            SandboxForkResponse: Sandbox Fork Response

        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)

        url = f"{self.base_url}/sandbox/{id_}/fork"

        json_body: SandboxForkRequest | None = DataclassSerializer.serialize(body)

        response = await self._transport.request(
            "POST", url, params=None, json=json_body, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), SandboxForkResponse)
            case _:
                raise HTTPError(
                    response=response,
                    message="Unhandled status code",
                    status_code=response.status_code,
                )
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover
