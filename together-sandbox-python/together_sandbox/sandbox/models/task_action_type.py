from enum import Enum


class TaskActionType(str, Enum):
    RESTART = "restart"
    START = "start"
    STOP = "stop"

    def __str__(self) -> str:
        return str(self.value)
