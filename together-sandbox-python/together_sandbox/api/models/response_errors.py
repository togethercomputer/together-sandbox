from typing import List, TypeAlias

from .response_errors_item import ResponseErrorsItem

from .response_errors_item import ResponseErrorsItem

__all__ = ['ResponseErrors']

ResponseErrors: TypeAlias = List[ResponseErrorsItem]