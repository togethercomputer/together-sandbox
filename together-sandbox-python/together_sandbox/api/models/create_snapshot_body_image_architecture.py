from enum import Enum


class CreateSnapshotBodyImageArchitecture(str, Enum):
    AMD64 = "amd64"
    ARM64 = "arm64"

    def __str__(self) -> str:
        return str(self.value)
