from enum import Enum


class SandboxlistStatus(str, Enum):
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
