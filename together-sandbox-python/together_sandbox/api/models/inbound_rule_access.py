from enum import Enum


class InboundRuleAccess(str, Enum):
    ALLOW = "allow"
    ALLOW_WITH_TOKEN = "allow_with_token"
    DENY = "deny"

    def __str__(self) -> str:
        return str(self.value)
