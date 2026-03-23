from typing import Protocol, runtime_checkable

from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.utils import DataclassSerializer

from ..models.template_create_request_common import TemplateCreateRequestCommon
from ..models.template_create_response import TemplateCreateResponse


@runtime_checkable
class TemplatesClientProtocol(Protocol):
    """Protocol defining the interface of TemplatesClient for dependency injection."""

    async def templates_create(
        self,
        body: TemplateCreateRequestCommon | None = None,
    ) -> TemplateCreateResponse: ...


class TemplatesClient(TemplatesClientProtocol):
    """Client for templates endpoints. Uses HttpTransport for all HTTP and header management."""

    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url

    async def templates_create(
        self,
        body: TemplateCreateRequestCommon | None = None,
    ) -> TemplateCreateResponse:
        """
        Create a template

        Create a new template in the current workspace (creates 3 sandboxes and tags them)

        Args:
            body (TemplateCreateRequestCommon | None)
                                     : Template Create Request (json)

        Returns:
            TemplateCreateResponse: Template Create Response

        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/templates"

        json_body: TemplateCreateRequestCommon | None = DataclassSerializer.serialize(
            body
        )

        response = await self._transport.request(
            "POST", url, params=None, json=json_body, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), TemplateCreateResponse)
            case _:
                raise HTTPError(
                    response=response,
                    message="Unhandled status code",
                    status_code=response.status_code,
                )
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover
