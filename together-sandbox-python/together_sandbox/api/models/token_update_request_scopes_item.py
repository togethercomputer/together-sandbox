from enum import Enum


class TokenUpdateRequestScopesItem(str, Enum):
    SANDBOX_CREATE = "sandbox_create"
    SANDBOX_EDIT_CODE = "sandbox_edit_code"
    SANDBOX_READ = "sandbox_read"
    VM_MANAGE = "vm_manage"

    def __str__(self) -> str:
        return str(self.value)
