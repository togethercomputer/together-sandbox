from enum import StrEnum


class SandboxStatus(StrEnum):
    FAILED_TO_START = "failed_to_start"
    RECOVERING = "recovering"
    RUNNING = "running"
    STARTING = "starting"
    TERMINATED = "terminated"
    TERMINATING = "terminating"
    UNRECOVERED = "unrecovered"

    def __str__(self) -> str:
        return str(self.value)
