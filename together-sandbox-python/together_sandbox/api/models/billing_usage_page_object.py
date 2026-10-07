from enum import Enum


class BillingUsagePageObject(str, Enum):
    BILLING_USAGE_REPORT = "billing.usage_report"

    def __str__(self) -> str:
        return str(self.value)
