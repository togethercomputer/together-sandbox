from __future__ import annotations

from typing import TypeVar
import base64
import re
from .api.models import Error as ApiError
from .sandbox.models.error import Error as SandboxError
from .api.models.sandbox import Sandbox as SandboxModel

_CSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def _strip_ansi(s: str) -> str:
    return _CSI_RE.sub("", s)


def _base32_encode(s: str) -> str:
    return base64.b32encode(s.encode()).decode().lower().rstrip("=")


_T = TypeVar("_T")


def _unwrap_or_raise(
    result: _T | ApiError | SandboxError | None, *, op: str, context: str = ""
) -> _T:
    suffix = f" {context}" if context else ""
    if result is None:
        raise RuntimeError(f"{op} returned None{suffix}")
    if isinstance(result, ApiError) | isinstance(result, SandboxError):
        raise RuntimeError(
            f"Failed to {op}{suffix}: {result.message} (code: {result.code})"
        )
    return result


def _resolve_connection(sandbox: SandboxModel) -> tuple[str, str]:
    """
    Extract the agent connection details from the Sandbox model.
    """
    if not sandbox.agent_url or not sandbox.agent_token:
        raise RuntimeError("Sandbox has no agent connection details")
    return sandbox.agent_url, sandbox.agent_token
