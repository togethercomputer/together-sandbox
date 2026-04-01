from enum import Enum


class VMCreateSessionRequestPermission(str, Enum):
    READ = "read"
    WRITE = "write"

    def __str__(self) -> str:
        return str(self.value)
