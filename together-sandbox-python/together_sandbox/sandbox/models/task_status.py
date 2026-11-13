from enum import StrEnum


class TaskStatus(StrEnum):
    ERROR = "ERROR"
    FINISHED = "FINISHED"
    IDLE = "IDLE"
    KILLED = "KILLED"
    RESTARTING = "RESTARTING"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
