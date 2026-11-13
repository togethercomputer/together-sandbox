from enum import StrEnum


class TaskActionType(StrEnum):
    RESTART = "restart"
    START = "start"
    STOP = "stop"

    def __str__(self) -> str:
        return str(self.value)
