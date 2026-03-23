from typing import Protocol, runtime_checkable

from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport

from ..models.meta_information import MetaInformation


@runtime_checkable
class MetaClientProtocol(Protocol):
    """Protocol defining the interface of MetaClient for dependency injection."""

    async def meta_info(
        self,
    ) -> MetaInformation: ...


class MetaClient(MetaClientProtocol):
    """Client for meta endpoints. Uses HttpTransport for all HTTP and header management."""

    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url

    async def meta_info(
        self,
    ) -> MetaInformation:
        """
        Metadata about the API

        Returns:
            MetaInformation: Meta Info Response

        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/meta/info"

        response = await self._transport.request(
            "GET", url, params=None, json=None, data=None, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), MetaInformation)
            case _:
                raise HTTPError(
                    response=response,
                    message="Unhandled status code",
                    status_code=response.status_code,
                )
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover
