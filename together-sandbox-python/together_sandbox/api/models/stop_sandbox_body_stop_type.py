from enum import Enum


class StopSandboxBodyStopType(str, Enum):
    HIBERNATE = "hibernate"
    SHUTDOWN = "shutdown"

    def __str__(self) -> str:
        return str(self.value)
