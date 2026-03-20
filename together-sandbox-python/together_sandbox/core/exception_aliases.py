from httpx import Response
from together_sandbox.core.exceptions import ClientError, HTTPError, ServerError


class Error101(HTTPError):
    """HTTP 101 Switching Protocols.

Raised when the server responds with a 101 status code (e.g. WebSocket upgrade)."""
    def __init__(self, response: Response) -> None:
        """Initialise Error101 with the HTTP response.

        Args:
            response: The httpx Response object that triggered this exception
        """
        super().__init__(status_code=response.status_code, message=response.text, response=response)


class BadRequestError(ClientError):
    """HTTP 400 Bad Request.

Raised when the server responds with a 400 status code."""
    def __init__(self, response: Response) -> None:
        """Initialise BadRequestError with the HTTP response.

        Args:
            response: The httpx Response object that triggered this exception
        """
        super().__init__(status_code=response.status_code, message=response.text, response=response)


class UnauthorisedError(ClientError):
    """HTTP 401 Unauthorised.

Raised when the server responds with a 401 status code."""
    def __init__(self, response: Response) -> None:
        """Initialise UnauthorisedError with the HTTP response.

        Args:
            response: The httpx Response object that triggered this exception
        """
        super().__init__(status_code=response.status_code, message=response.text, response=response)


class NotFoundError(ClientError):
    """HTTP 404 Not Found.

Raised when the server responds with a 404 status code."""
    def __init__(self, response: Response) -> None:
        """Initialise NotFoundError with the HTTP response.

        Args:
            response: The httpx Response object that triggered this exception
        """
        super().__init__(status_code=response.status_code, message=response.text, response=response)


class ConflictError(ClientError):
    """HTTP 409 Conflict.

Raised when the server responds with a 409 status code."""
    def __init__(self, response: Response) -> None:
        """Initialise ConflictError with the HTTP response.

        Args:
            response: The httpx Response object that triggered this exception
        """
        super().__init__(status_code=response.status_code, message=response.text, response=response)


class InternalServerError(ServerError):
    """HTTP 500 Internal Server Error.

Raised when the server responds with a 500 status code."""
    def __init__(self, response: Response) -> None:
        """Initialise InternalServerError with the HTTP response.

        Args:
            response: The httpx Response object that triggered this exception
        """
        super().__init__(status_code=response.status_code, message=response.text, response=response)


__all__ = ["BadRequestError", "ConflictError", "Error101", "InternalServerError", "NotFoundError", "UnauthorisedError"]
