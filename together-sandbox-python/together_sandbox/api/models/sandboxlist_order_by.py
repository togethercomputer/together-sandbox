from enum import Enum


class SandboxlistOrderBy(str, Enum):
    INSERTED_AT = "inserted_at"
    UPDATED_AT = "updated_at"

    def __str__(self) -> str:
        return str(self.value)
