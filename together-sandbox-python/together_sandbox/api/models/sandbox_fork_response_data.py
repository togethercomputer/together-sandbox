from __future__ import annotations

from dataclasses import dataclass

from .sandbox_fork_response_data_start_response import SandboxForkResponseDataStartResponse

__all__ = ["SandboxForkResponseData"]

@dataclass
class SandboxForkResponseData:
    """
    SandboxForkResponseData dataclass
    
    Args:
        alias (str)              : 
        id_ (str)                : Maps from 'id'
        title (str | None)       : 
        start_response (SandboxForkResponseDataStartResponse | None)
                                 : VM start response. Only present when start_options were
                                   provided in the request.
    """
    alias: str
    id_: str  # Maps from 'id'
    title: str | None
    start_response: SandboxForkResponseDataStartResponse | None = None  # VM start response. Only present when start_options were provided in the request.
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "alias": "alias",
            "id": "id_",
            "start_response": "start_response",
            "title": "title",
        }
        key_transform_with_dump = {
            "alias": "alias",
            "id_": "id",
            "start_response": "start_response",
            "title": "title",
        }