from enum import Enum


class SandboxVersionType(str, Enum):
    SANDBOX_VERSION = "sandbox_version"

    def __str__(self) -> str:
        return str(self.value)
