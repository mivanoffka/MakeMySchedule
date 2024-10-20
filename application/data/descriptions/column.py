from typing import Optional


class ColumnDescription:
    _attribute: str
    _size: int

    @property
    def attribute(self):
        return self._attribute

    @property
    def displayed_name(self):
        return self._displayed_name

    def __init__(self, attribute: str, displayed_name: Optional[str] = None):
        self._attribute = attribute
        self._displayed_name = displayed_name if displayed_name else attribute