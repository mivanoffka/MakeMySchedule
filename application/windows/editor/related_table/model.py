from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtWidgets import QItemDelegate, QComboBox, QAbstractItemView, QWidget, QVBoxLayout, QTableView, \
    QHeaderView, QPushButton, QHBoxLayout, QDialogButtonBox, QDialog


class RelatedTableModel(QAbstractTableModel):
    def __init__(self, session, related_description, parent=None):
        super().__init__(parent)
        self.current_object = None
        self.session = session
        self.related_description = related_description
        self.data_rows = []
        self.header = related_description.displayed_name

    def rowCount(self, parent=None):
        return len(self.data_rows)

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            obj = self.data_rows[index.row()]
            # Если объект None, то возвращаем пустую строку для отображения пустой записи
            return "" if obj is None else self.related_description.represent(obj)
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            selected_object = value

            if selected_object is not None and self.current_object:
                if selected_object in self.data_rows:
                    return False

                if self.data_rows[index.row()] is None:
                    self.data_rows[index.row()] = value
                    getattr(self.current_object, self.related_description.attribute).append(selected_object)
                else:
                    getattr(self.current_object, self.related_description.attribute)[index.row()] = selected_object
                    self.data_rows[index.row()] = value

                self.session.commit()
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return True
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.header
        return None

    def update_data(self, selected_object):
        """Обновляет данные таблицы на основе связанных объектов."""
        self.beginResetModel()
        if selected_object:
            self.current_object = selected_object
            related_objects = getattr(selected_object, self.related_description.attribute)
            self.data_rows = list(related_objects)  # Копируем объекты
        else:
            self.current_object = None
            self.data_rows = []
        self.endResetModel()

    def add_empty_row(self):
        """Добавляет пустую строку в конец таблицы."""
        self.beginInsertRows(self.index(len(self.data_rows), 0), len(self.data_rows), len(self.data_rows))
        self.data_rows.append(None)  # Добавляем None как пустую запись
        self.endInsertRows()