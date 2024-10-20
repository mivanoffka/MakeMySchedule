from typing import List, Optional

from .column import ColumnDescription
from .foreign import ForeignKeyColumnDescription
from .list import ListColumnDescription


class TableDescription:
    _columns: List[ColumnDescription]
    _displayed_name: str

    def filter_columns(self):
        return tuple(column for column in self.foreign_columns() if column.as_filter)

    def foreign_columns(self):
        return tuple(column for column in self._columns if isinstance(column, ForeignKeyColumnDescription))

    def regular_columns(self):
        return tuple(column for column in self._columns if not isinstance(column, ListColumnDescription))

    def list_columns(self):
        return tuple(column for column in self._columns if isinstance(column, ListColumnDescription))

    @property
    def displayed_name(self):
        return self._displayed_name

    def __init__(self, displayed_name: Optional[str] = None, *columns: ColumnDescription):
        self._columns = [*columns]
        self._displayed_name = displayed_name