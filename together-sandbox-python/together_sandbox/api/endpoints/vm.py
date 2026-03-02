from typing import Any, Callable, NoReturn, Optional, Protocol, cast, runtime_checkable

from ..models.vm_assign_tag_alias_request_2 import VmAssignTagAliasRequest2
from ..models.vm_assign_tag_alias_response_2 import VmAssignTagAliasResponse2
from ..models.vm_create_session_request_2 import VmCreateSessionRequest2
from ..models.vm_create_session_response_2 import VmCreateSessionResponse2
from ..models.vm_create_tag_request_2 import VmCreateTagRequest2
from ..models.vm_create_tag_response_2 import VmCreateTagResponse2
from ..models.vm_delete_response_2 import VmDeleteResponse2
from ..models.vm_hibernate_request_2 import VmHibernateRequest2
from ..models.vm_hibernate_response_2 import VmHibernateResponse2
from ..models.vm_list_clusters_response_2 import VmListClustersResponse2
from ..models.vm_list_running_v_ms_response_2 import VmListRunningVMsResponse2
from ..models.vm_shutdown_request_2 import VmShutdownRequest2
from ..models.vm_shutdown_response_2 import VmShutdownResponse2
from ..models.vm_start_request_2 import VmStartRequest2
from ..models.vm_start_response_2 import VmStartResponse2
from ..models.vm_update_hibernation_timeout_request_2 import VmUpdateHibernationTimeoutRequest2
from ..models.vm_update_hibernation_timeout_response_2 import VmUpdateHibernationTimeoutResponse2
from ..models.vm_update_specs_request_2 import VmUpdateSpecsRequest2
from ..models.vm_update_specs_response_2 import VmUpdateSpecsResponse2
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_bytes
from together_sandbox.core.utils import DataclassSerializer

@runtime_checkable
class VmClientProtocol(Protocol):
    """Protocol defining the interface of VmClient for dependency injection."""
    
    async def vm_assign_tag_alias(
    self,
    namespace: str,
    alias: str,
    body: VmAssignTagAliasRequest2 | None = None,
    ) -> VmAssignTagAliasResponse2: ...
    
    async def vm_list_clusters(
    self,
    ) -> VmListClustersResponse2: ...
    
    async def vm_list_running_vms(
    self,
    ) -> VmListRunningVMsResponse2: ...
    
    async def vm_create_tag(
    self,
    body: VmCreateTagRequest2 | None = None,
    ) -> VmCreateTagResponse2: ...
    
    async def vm_delete(
    self,
    id_: str,
    ) -> VmDeleteResponse2: ...
    
    async def vm_hibernate(
    self,
    id_: str,
    body: VmHibernateRequest2 | None = None,
    ) -> VmHibernateResponse2: ...
    
    async def vm_update_hibernation_timeout(
    self,
    id_: str,
    body: VmUpdateHibernationTimeoutRequest2 | None = None,
    ) -> VmUpdateHibernationTimeoutResponse2: ...
    
    async def vm_create_session(
    self,
    id_: str,
    body: VmCreateSessionRequest2 | None = None,
    ) -> VmCreateSessionResponse2: ...
    
    async def vm_shutdown(
    self,
    id_: str,
    body: VmShutdownRequest2 | None = None,
    ) -> VmShutdownResponse2: ...
    
    async def vm_update_specs(
    self,
    id_: str,
    body: VmUpdateSpecsRequest2 | None = None,
    ) -> VmUpdateSpecsResponse2: ...
    
    async def vm_start(
    self,
    id_: str,
    body: VmStartRequest2 | None = None,
    ) -> VmStartResponse2: ...
    
    async def vm_update_specs_2(
    self,
    id_: str,
    body: VmUpdateSpecsRequest2 | None = None,
    ) -> VmUpdateSpecsResponse2: ...
    


class VmClient(VmClientProtocol):
    """Client for vm endpoints. Uses HttpTransport for all HTTP and header management."""
    
    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url
    
    async def vm_assign_tag_alias(
        self,
        namespace: str,
        alias: str,
        body: VmAssignTagAliasRequest2 | None = None,
    ) -> VmAssignTagAliasResponse2:
        """
        Assign a tag alias to a VM tag
        
        Assign a tag alias to a VM tag.
        
        Args:
            namespace (str)          : Tag alias namespace
            alias (str)              : Tag alias
            body (VmAssignTagAliasRequest2 | None)
                                     : VM Assign Tag Alias Request (json)
        
        Returns:
            VmAssignTagAliasResponse2: VM Assign Tag Alias Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        namespace = DataclassSerializer.serialize(namespace)
        alias = DataclassSerializer.serialize(alias)
        
        url = f"{self.base_url}/vm/alias/{namespace}/{alias}"
        
        json_body: VmAssignTagAliasRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("PUT", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmAssignTagAliasResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_list_clusters(
        self,
    ) -> VmListClustersResponse2:
        """
        List all available clusters
        
        List all available clusters.
        
        Returns:
            VmListClustersResponse2: VM List Clusters Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/vm/clusters"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmListClustersResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_list_running_vms(
        self,
    ) -> VmListRunningVMsResponse2:
        """
        List information about currently running VMs
        
        List information about currently running VMs. This information is updated roughly every
        30 seconds, so this data is not guaranteed to be perfectly up-to-date.
        
        Returns:
            VmListRunningVMsResponse2: VM List Running VMs Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/vm/running"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmListRunningVMsResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_create_tag(
        self,
        body: VmCreateTagRequest2 | None = None,
    ) -> VmCreateTagResponse2:
        """
        Create a new tag for a VM
        
        Creates a new tag for a VM.
        
        Args:
            body (VmCreateTagRequest2 | None)
                                     : VM Create Tag Request (json)
        
        Returns:
            VmCreateTagResponse2: VM Create Tag Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        url = f"{self.base_url}/vm/tag"
        
        json_body: VmCreateTagRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmCreateTagResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_delete(
        self,
        id_: str,
    ) -> VmDeleteResponse2:
        """
        Delete a VM
        
        Deletes a VM, permanently removing it from the system.  This endpoint can only be used
        on VMs that belong to your team's workspace. Deleting a VM is irreversible and will
        permanently delete all data associated with it.
        
        Args:
            id (str)                 : Sandbox ID
        
        Returns:
            VmDeleteResponse2: VM Delete Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}"
        
        response = await self._transport.request(
            "DELETE", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmDeleteResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_hibernate(
        self,
        id_: str,
        body: VmHibernateRequest2 | None = None,
    ) -> VmHibernateResponse2:
        """
        Hibernate a VM
        
        Suspends a running VM, saving a snapshot of its memory and running processes  This
        endpoint may take an extended amount of time to return (30 seconds). If the VM is not
        currently running, it will return an error (404).  Unless later shut down by request or
        due to inactivity, a hibernated VM can be resumed with minimal latency.
        
        Args:
            id (str)                 : Sandbox ID
            body (VmHibernateRequest2 | None)
                                     : VM Hibernate Request (json)
        
        Returns:
            VmHibernateResponse2: VM Hibernate Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}/hibernate"
        
        json_body: VmHibernateRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmHibernateResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_update_hibernation_timeout(
        self,
        id_: str,
        body: VmUpdateHibernationTimeoutRequest2 | None = None,
    ) -> VmUpdateHibernationTimeoutResponse2:
        """
        Update VM Hibernation Timeout
        
        Updates the hibernation timeout of a running VM.  This endpoint can only be used on VMs
        that belong to your team's workspace. The new timeout must be greater than 0 and less
        than or equal to 86400 seconds (24 hours).
        
        Args:
            id (str)                 : Sandbox ID
            body (VmUpdateHibernationTimeoutRequest2 | None)
                                     : VM Update Hibernation Timeout Request (json)
        
        Returns:
            VmUpdateHibernationTimeoutResponse2: VM Update Hibernation Timeout Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}/hibernation_timeout"
        
        json_body: VmUpdateHibernationTimeoutRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("PUT", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmUpdateHibernationTimeoutResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_create_session(
        self,
        id_: str,
        body: VmCreateSessionRequest2 | None = None,
    ) -> VmCreateSessionResponse2:
        """
        Create a new session on a VM
        
        Creates a new session on a running VM. A session represents an isolated Linux user, with
        their own container. A session has a single use token that the user can use to connect
        to the VM. This token has specific permissions (currently, read or write). The session
        is identified by a unique session ID, and the Linux username is based on the session ID.
        The Git user name and email can be configured via parameters.  This endpoint requires
        the VM to be running. If the VM is not running, it will return a 404 error.
        
        Args:
            id (str)                 : Sandbox ID
            body (VmCreateSessionRequest2 | None)
                                     : VM Create Session Request (json)
        
        Returns:
            VmCreateSessionResponse2: VM Create Session Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}/sessions"
        
        json_body: VmCreateSessionRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmCreateSessionResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_shutdown(
        self,
        id_: str,
        body: VmShutdownRequest2 | None = None,
    ) -> VmShutdownResponse2:
        """
        Shutdown a VM
        
        Stops a running VM, ending all currently running processes  This endpoint may take an
        extended amount of time to return (30 seconds). If the VM is not currently running, it
        will return an error (404).  Shutdown VMs require additional time to start up.
        
        Args:
            id (str)                 : Sandbox ID
            body (VmShutdownRequest2 | None)
                                     : VM Shutdown Request (json)
        
        Returns:
            VmShutdownResponse2: VM Shutdown Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}/shutdown"
        
        json_body: VmShutdownRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmShutdownResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_update_specs(
        self,
        id_: str,
        body: VmUpdateSpecsRequest2 | None = None,
    ) -> VmUpdateSpecsResponse2:
        """
        Update VM Specs
        
        Updates the specifications (CPU, memory, storage) of a running VM.  This endpoint can
        only be used on VMs that belong to your team's workspace. The new tier must not exceed
        your team's maximum allowed tier.
        
        Args:
            id (str)                 : Sandbox ID
            body (VmUpdateSpecsRequest2 | None)
                                     : VM Update Specs Request (json)
        
        Returns:
            VmUpdateSpecsResponse2: VM Update Specs Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}/specs"
        
        json_body: VmUpdateSpecsRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("PUT", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmUpdateSpecsResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_start(
        self,
        id_: str,
        body: VmStartRequest2 | None = None,
    ) -> VmStartResponse2:
        """
        Start a VM
        
        Start a virtual machine for the sandbox (devbox) with the given ID  While the
        `sandbox:read` scope is required for this endpoint, the resulting VM will have
        permissions according to the `sandbox:edit_code` scope. If present, the returned token
        will have write permissions to the contents of the VM. Otherwise, the returned token
        will grant only read-only permissions.  This endpoint is subject to special rate limits
        related to concurrent VM usage.
        
        Args:
            id (str)                 : Sandbox ID
            body (VmStartRequest2 | None)
                                     : VM Start Request (json)
        
        Returns:
            VmStartResponse2: VM Start Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}/start"
        
        json_body: VmStartRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmStartResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def vm_update_specs_2(
        self,
        id_: str,
        body: VmUpdateSpecsRequest2 | None = None,
    ) -> VmUpdateSpecsResponse2:
        """
        Update VM Specs
        
        Updates the specifications (CPU, memory, storage) of a running VM.  This endpoint can
        only be used on VMs that belong to your team's workspace. The new tier must not exceed
        your team's maximum allowed tier.
        
        Args:
            id (str)                 : Sandbox ID
            body (VmUpdateSpecsRequest2 | None)
                                     : VM Update Specs Request (json)
        
        Returns:
            VmUpdateSpecsResponse2: VM Update Specs Response
        
        Raises:
            HttpError:
                HTTPError: If the server returns a non-2xx HTTP response.
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/vm/{id_}/update_specs"
        
        json_body: VmUpdateSpecsRequest2 | None = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), VmUpdateSpecsResponse2)
            case _:
                raise HTTPError(response=response, message="Unhandled status code", status_code=response.status_code)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover