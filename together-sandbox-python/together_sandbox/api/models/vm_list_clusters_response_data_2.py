from dataclasses import dataclass

from .vm_list_clusters_response_data_clusters import VmListClustersResponseDataClusters

__all__ = ["VmListClustersResponseData2"]

@dataclass
class VmListClustersResponseData2:
    """
    VmListClustersResponseData2 dataclass
    
    Args:
        clusters (VmListClustersResponseDataClusters)
                                 : 
    """
    clusters: VmListClustersResponseDataClusters
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "clusters": "clusters",
        }
        key_transform_with_dump = {
            "clusters": "clusters",
        }