from dataclasses import dataclass

__all__ = ["SandboxListResponseDataPagination"]

@dataclass
class SandboxListResponseDataPagination:
    """
    SandboxListResponseDataPagination dataclass
    
    Args:
        current_page (int)       : 
        next_page (int | None)   : The number of the next page, if any. If `null`, the
                                   current page is the last page of records.
        total_records (int)      : 
    """
    current_page: int
    next_page: int | None  # The number of the next page, if any. If `null`, the current page is the last page of records.
    total_records: int
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "current_page": "current_page",
            "next_page": "next_page",
            "total_records": "total_records",
        }
        key_transform_with_dump = {
            "current_page": "current_page",
            "next_page": "next_page",
            "total_records": "total_records",
        }