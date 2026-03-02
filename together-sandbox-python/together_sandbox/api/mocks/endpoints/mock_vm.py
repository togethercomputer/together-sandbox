from typing import Any, NoReturn, TYPE_CHECKING

from ...models.vm_assign_tag_alias_request_2 import VmAssignTagAliasRequest2
from ...models.vm_assign_tag_alias_response_2 import VmAssignTagAliasResponse2
from ...models.vm_create_session_request_2 import VmCreateSessionRequest2
from ...models.vm_create_session_response_2 import VmCreateSessionResponse2
from ...models.vm_create_tag_request_2 import VmCreateTagRequest2
from ...models.vm_create_tag_response_2 import VmCreateTagResponse2
from ...models.vm_delete_response_2 import VmDeleteResponse2
from ...models.vm_hibernate_request_2 import VmHibernateRequest2
from ...models.vm_hibernate_response_2 import VmHibernateResponse2
from ...models.vm_list_clusters_response_2 import VmListClustersResponse2
from ...models.vm_list_running_v_ms_response_2 import VmListRunningVMsResponse2
from ...models.vm_shutdown_request_2 import VmShutdownRequest2
from ...models.vm_shutdown_response_2 import VmShutdownResponse2
from ...models.vm_start_request_2 import VmStartRequest2
from ...models.vm_start_response_2 import VmStartResponse2
from ...models.vm_update_hibernation_timeout_request_2 import VmUpdateHibernationTimeoutRequest2
from ...models.vm_update_hibernation_timeout_response_2 import VmUpdateHibernationTimeoutResponse2
from ...models.vm_update_specs_request_2 import VmUpdateSpecsRequest2
from ...models.vm_update_specs_response_2 import VmUpdateSpecsResponse2
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.utils import DataclassSerializer

if TYPE_CHECKING:
    from ...endpoints.vm import VmClientProtocol

class MockVmClient:
    """
    Mock implementation of VmClient for testing.
    
    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.
    
    Example:
        class TestVmClient(MockVmClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """
    
    async def vm_assign_tag_alias(
    self,
    namespace: str,
    alias: str,
    body: VmAssignTagAliasRequest2 | None = None,
    ) -> VmAssignTagAliasResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_assign_tag_alias() not implemented. Override this method in your test subclass.")
    
    
    async def vm_list_clusters(
    self,
    ) -> VmListClustersResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_list_clusters() not implemented. Override this method in your test subclass.")
    
    
    async def vm_list_running_vms(
    self,
    ) -> VmListRunningVMsResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_list_running_vms() not implemented. Override this method in your test subclass.")
    
    
    async def vm_create_tag(
    self,
    body: VmCreateTagRequest2 | None = None,
    ) -> VmCreateTagResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_create_tag() not implemented. Override this method in your test subclass.")
    
    
    async def vm_delete(
    self,
    id_: str,
    ) -> VmDeleteResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_delete() not implemented. Override this method in your test subclass.")
    
    
    async def vm_hibernate(
    self,
    id_: str,
    body: VmHibernateRequest2 | None = None,
    ) -> VmHibernateResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_hibernate() not implemented. Override this method in your test subclass.")
    
    
    async def vm_update_hibernation_timeout(
    self,
    id_: str,
    body: VmUpdateHibernationTimeoutRequest2 | None = None,
    ) -> VmUpdateHibernationTimeoutResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_update_hibernation_timeout() not implemented. Override this method in your test subclass.")
    
    
    async def vm_create_session(
    self,
    id_: str,
    body: VmCreateSessionRequest2 | None = None,
    ) -> VmCreateSessionResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_create_session() not implemented. Override this method in your test subclass.")
    
    
    async def vm_shutdown(
    self,
    id_: str,
    body: VmShutdownRequest2 | None = None,
    ) -> VmShutdownResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_shutdown() not implemented. Override this method in your test subclass.")
    
    
    async def vm_update_specs(
    self,
    id_: str,
    body: VmUpdateSpecsRequest2 | None = None,
    ) -> VmUpdateSpecsResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_update_specs() not implemented. Override this method in your test subclass.")
    
    
    async def vm_start(
    self,
    id_: str,
    body: VmStartRequest2 | None = None,
    ) -> VmStartResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_start() not implemented. Override this method in your test subclass.")
    
    
    async def vm_update_specs_2(
    self,
    id_: str,
    body: VmUpdateSpecsRequest2 | None = None,
    ) -> VmUpdateSpecsResponse2:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockVmClient.vm_update_specs_2() not implemented. Override this method in your test subclass.")