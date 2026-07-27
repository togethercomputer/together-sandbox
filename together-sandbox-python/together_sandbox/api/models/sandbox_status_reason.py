from enum import Enum


class SandboxStatusReason(str, Enum):
    AUTOTERMINATED = "autoterminated"
    CLUSTER_LOST = "cluster_lost"
    COLD_STARTED = "cold_started"
    COLD_START_REQUESTED = "cold_start_requested"
    CRASHED = "crashed"
    EVICTED = "evicted"
    INTERNAL_ERROR = "internal_error"
    NODE_LOST = "node_lost"
    OOM_KILLED = "oom_killed"
    OUT_OF_CAPACITY = "out_of_capacity"
    RESTORED = "restored"
    RESTORE_REQUESTED = "restore_requested"
    TERMINATION_REQUESTED = "termination_requested"

    def __str__(self) -> str:
        return str(self.value)
