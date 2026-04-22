from enum import Enum


class SandboxStopReasonType2Type1(str, Enum):
    CLUSTER_LOST = "cluster_lost"
    CRASHED = "crashed"
    EVICTED = "evicted"
    HIBERNATED = "hibernated"
    NODE_LOST = "node_lost"
    OOM_KILLED = "oom_killed"
    SHUTDOWN = "shutdown"
    START_FAILED = "start_failed"

    def __str__(self) -> str:
        return str(self.value)
