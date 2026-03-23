from enum import Enum


class FileActionRequestAction(str, Enum):
    COPY = "copy"
    MOVE = "move"

    def __str__(self) -> str:
        return str(self.value)
