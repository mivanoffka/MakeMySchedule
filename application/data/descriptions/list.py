from typing import Any, Optional, Callable

from .column import ColumnDescription


class ListColumnDescription(ColumnDescription):
    _related_orm_type: Any

    @property
    def orm_type(self):
        return self._related_orm_type

    @staticmethod
    def represent_by_default(obj: Any):
        if hasattr(obj, "name"):
            return getattr(obj, "name")
        elif hasattr(obj, "value"):
            return getattr(obj, "value")
        else:
            return getattr(obj, "id")

    def __init__(self, content_orm_type: Any, attribute: str,
                 displayed_name: Optional[str] = None,
                 represent: Callable = None, size: Optional[int] = None):
        super().__init__(attribute, displayed_name)
        self._related_orm_type = content_orm_type
        self.represent = represent if represent else self.represent_by_default
        self._size = size if size else 1