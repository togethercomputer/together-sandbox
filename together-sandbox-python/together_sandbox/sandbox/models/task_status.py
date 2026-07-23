from enum import Enum


class TaskStatus(str, Enum):
    ERROR = "ERROR"
    FINISHED = "FINISHED"
    IDLE = "IDLE"
    KILLED = "KILLED"
    RESTARTING = "RESTARTING"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
