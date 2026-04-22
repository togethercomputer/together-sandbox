from enum import Enum


class SnapshotType(str, Enum):
    SNAPSHOT = "snapshot"

    def __str__(self) -> str:
        return str(self.value)
