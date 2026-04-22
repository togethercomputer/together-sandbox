from enum import Enum


class SandboxStartTypeType2Type1(str, Enum):
    COLD_START = "cold_start"
    RESUME = "resume"

    def __str__(self) -> str:
        return str(self.value)
