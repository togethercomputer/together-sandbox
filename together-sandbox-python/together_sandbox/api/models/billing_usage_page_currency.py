from enum import Enum


class BillingUsagePageCurrency(str, Enum):
    USD = "USD"

    def __str__(self) -> str:
        return str(self.value)
