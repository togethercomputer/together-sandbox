from enum import Enum


class SnapshotAliasType(str, Enum):
    SNAPSHOT_ALIAS = "snapshot_alias"

    def __str__(self) -> str:
        return str(self.value)
