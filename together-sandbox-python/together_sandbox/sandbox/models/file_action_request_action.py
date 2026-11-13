from enum import StrEnum


class FileActionRequestAction(StrEnum):
    COPY = "copy"
    MOVE = "move"

    def __str__(self) -> str:
        return str(self.value)
