from enum import Enum


class SandboxForkRequestStartOptionsTier(str, Enum):
    LARGE = "Large"
    MEDIUM = "Medium"
    MICRO = "Micro"
    NANO = "Nano"
    PICO = "Pico"
    SMALL = "Small"
    XLARGE = "XLarge"

    def __str__(self) -> str:
        return str(self.value)
