from dataclasses import dataclass

__all__ = ["VmAssignTagAliasResponseData2"]

@dataclass
class VmAssignTagAliasResponseData2:
    """
    VmAssignTagAliasResponseData2 dataclass
    
    Args:
        alias (str)              : 
        namespace (str)          : 
        tag_alias_id (str)       : 
        tag_id (str)             : 
        team_id (str)            : 
    """
    alias: str
    namespace: str
    tag_alias_id: str
    tag_id: str
    team_id: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "alias": "alias",
            "namespace": "namespace",
            "tag_alias_id": "tag_alias_id",
            "tag_id": "tag_id",
            "team_id": "team_id",
        }
        key_transform_with_dump = {
            "alias": "alias",
            "namespace": "namespace",
            "tag_alias_id": "tag_alias_id",
            "tag_id": "tag_id",
            "team_id": "team_id",
        }