from typing import Any, Optional, Callable
from .column import ColumnDescription


class ForeignKeyColumnDescription(ColumnDescription):
    @property
    def as_filter(self) -> bool:
        return self._filter_mode

    @property
    def orm_type(self):
        return self._orm_type

    @staticmethod
    def represent_by_default(obj: Any):
        if hasattr(obj, "name"):
            return getattr(obj, "name")
        elif hasattr(obj, "value"):
            return getattr(obj, "value")
        else:
            return getattr(obj, "id")

    def __init__(self, orm_type: Any, attribute: str,

                 displayed_name: Optional[str] = None,
                 represent: Callable = None,
                 as_filter = False):
        super().__init__(attribute, displayed_name)
        self._orm_type = orm_type
        self._filter_mode = as_filter
        self.represent = represent if represent else self.represent_by_default