from enum import Enum


class SandboxRecoveryStatusType2Type1(str, Enum):
    CANCELED = "canceled"
    PENDING = "pending"
    RECOVERED = "recovered"
    UNRECOVERABLE = "unrecoverable"

    def __str__(self) -> str:
        return str(self.value)
