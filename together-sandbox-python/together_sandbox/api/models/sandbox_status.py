from enum import Enum


class SandboxStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    STARTING = "starting"
    STOPPED = "stopped"
    STOPPING = "stopping"

    def __str__(self) -> str:
        return str(self.value)
