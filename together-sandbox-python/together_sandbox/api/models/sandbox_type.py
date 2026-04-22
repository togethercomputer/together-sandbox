from enum import Enum


class SandboxType(str, Enum):
    SANDBOX = "sandbox"

    def __str__(self) -> str:
        return str(self.value)
