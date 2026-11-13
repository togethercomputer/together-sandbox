from enum import StrEnum


class WatcherEventType(StrEnum):
    ADD = "ADD"
    CHANGE = "CHANGE"
    CONNECTED = "connected"
    ERROR = "error"
    REMOVE = "REMOVE"

    def __str__(self) -> str:
        return str(self.value)
