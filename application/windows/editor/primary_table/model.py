from PySide6.QtCore import Qt, QAbstractTableModel
from ....data import ForeignKeyColumnDescription


class PrimaryTableModel(QAbstractTableModel):
    def __init__(self, session, orm_class, visible_columns, parent=None):
        super().__init__(parent)
        self.session = session
        self.orm_class = orm_class
        self.visible_columns = visible_columns
        self.data_rows = self._fetch_data()
        self.original_data_rows = self.data_rows.copy()

        self.filter = dict.fromkeys(self.visible_columns, None)

    def _fetch_data(self):
        return self.session.query(self.orm_class).all()

    def rowCount(self, parent=None):
        return len(self.data_rows)

    def columnCount(self, parent=None):
        return len(self.visible_columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            obj = self.data_rows[index.row()]
            column = self.visible_columns[index.column()]
            value = getattr(obj, column.attribute)

            if isinstance(column, ForeignKeyColumnDescription):
                related_obj = self.session.query(column.orm_type).filter_by(id=value).first()
                if related_obj:
                    return column.represent(related_obj)
                return ""

            return "" if value is None else str(value)
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            obj = self.data_rows[index.row()]
            column = self.visible_columns[index.column()]

            if isinstance(column, ForeignKeyColumnDescription):
                setattr(obj, column.attribute, value.id)
            else:
                setattr(obj, column.attribute, value)

            self.session.commit()
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.visible_columns[section].displayed_name  # Use attribute name as header
        return None

    def refresh(self):
        self.beginResetModel()
        self.data_rows = self._fetch_data()
        self.original_data_rows = self.data_rows.copy()
        self.endResetModel()

    def reset_data(self):
        """Reset data rows to the original unfiltered state."""
        self.beginResetModel()
        self.data_rows = self.original_data_rows.copy()  # Reset to original data
        self.filter = dict.fromkeys(self.visible_columns, None)  # Clear all filters
        self.endResetModel()

    def filter_data(self, filters):
        self.beginResetModel()

        for column, selected_value in filters.items():
            self.filter[column] = selected_value

        filtered_rows = self.original_data_rows

        for column, selected_value in self.filter.items():
            if selected_value is not None:
                if isinstance(column, ForeignKeyColumnDescription):
                    # # For foreign key columns, filter by related object
                    _all = self.session.query(column.orm_type).all()
                    _all_satisfied = [obj for obj in _all if column.represent(obj) == selected_value]
                    if _all_satisfied:
                        selected_obj = _all_satisfied[0]
                        filtered_rows = [row for row in filtered_rows if
                                         getattr(row, column.attribute) == selected_obj.id]
                    else:
                        filtered_rows = []
                else:
                    filtered_rows = [row for row in filtered_rows if
                                     getattr(row, column.attribute) == selected_value]

        self.data_rows = filtered_rows
        self.endResetModel()

    def update_data(self, new_data):
        """Update the data of the model."""
        self.beginResetModel()
        self.data_rows = new_data
        self.endResetModel()