from enum import Enum


class SandboxRequestedStopTypeType3Type1(str, Enum):
    HIBERNATE = "hibernate"
    SHUTDOWN = "shutdown"

    def __str__(self) -> str:
        return str(self.value)
