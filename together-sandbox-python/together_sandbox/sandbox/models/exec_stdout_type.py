from enum import StrEnum


class ExecStdoutType(StrEnum):
    STDERR = "stderr"
    STDOUT = "stdout"

    def __str__(self) -> str:
        return str(self.value)
