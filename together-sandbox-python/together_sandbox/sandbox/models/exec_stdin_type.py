from enum import Enum


class ExecStdinType(str, Enum):
    RESIZE = "resize"
    STDIN = "stdin"

    def __str__(self) -> str:
        return str(self.value)
