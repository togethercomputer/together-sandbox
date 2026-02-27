from enum import Enum


class UpdateExecRequestStatus(str, Enum):
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
