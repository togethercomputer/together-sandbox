from enum import StrEnum


class ExecStdinType(StrEnum):
    RESIZE = "resize"
    STDIN = "stdin"

    def __str__(self) -> str:
        return str(self.value)
