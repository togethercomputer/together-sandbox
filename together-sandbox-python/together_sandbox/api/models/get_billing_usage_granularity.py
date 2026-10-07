from enum import Enum


class GetBillingUsageGranularity(str, Enum):
    DAY = "day"
    HOUR = "hour"

    def __str__(self) -> str:
        return str(self.value)
