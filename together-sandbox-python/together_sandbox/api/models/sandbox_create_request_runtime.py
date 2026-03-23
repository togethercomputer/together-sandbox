from enum import Enum


class SandboxCreateRequestRuntime(str, Enum):
    BROWSER = "browser"
    VM = "vm"

    def __str__(self) -> str:
        return str(self.value)
