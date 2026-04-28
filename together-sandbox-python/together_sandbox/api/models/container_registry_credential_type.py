from enum import Enum


class ContainerRegistryCredentialType(str, Enum):
    CONTAINER_REGISTRY_CREDENTIAL = "container_registry_credential"

    def __str__(self) -> str:
        return str(self.value)
