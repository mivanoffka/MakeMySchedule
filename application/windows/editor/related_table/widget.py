from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtWidgets import QItemDelegate, QComboBox, QAbstractItemView, QWidget, QVBoxLayout, QTableView, \
    QHeaderView, QPushButton, QHBoxLayout, QDialogButtonBox, QDialog, QGroupBox

from .delegate import RelatedComboBoxDelegate
from .model import RelatedTableModel


class RelatedTableWidget(QWidget):
    """Виджет для отображения связанных объектов в виде таблицы с QComboBox."""
    def __init__(self, session, related_description, parent=None):
        super().__init__(parent)
        self.session = session
        self.related_description = related_description

        # Основной лэйаут
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.group_box = QGroupBox()
        self.layout.addWidget(self.group_box)

        # Создаем QTableView и модель для него

        self.table_view = QTableView()
        self.table_view.verticalHeader().setDefaultSectionSize(20)
        self.group_box.setLayout(QVBoxLayout())
        self.group_box.setTitle(related_description.displayed_name)
        self.model = RelatedTableModel(session=self.session, related_description=self.related_description)
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.group_box.layout().addWidget(self.table_view)
        self.group_box.layout().setSpacing(0)

        self.delegate = RelatedComboBoxDelegate(self.session, self.related_description)
        self.table_view.setItemDelegate(self.delegate)

        self._add_remove_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.remove_button = QPushButton("Удалить")
        self.add_button.clicked.connect(self.add_related_object)
        self.remove_button.clicked.connect(self.remove_related_object)
        self._add_remove_layout.addWidget(self.add_button)
        self._add_remove_layout.addWidget(self.remove_button)
        self.group_box.layout().addLayout(self._add_remove_layout)
        self._add_remove_layout.setSpacing(4)

        self.current_object = None

        self.set_widgets_enabled(False)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def update_table(self, selected_object):
        """Обновление таблицы на основе выбранного объекта."""
        self.current_object = selected_object

        if selected_object:
            self.model.update_data(selected_object)
            self.set_widgets_enabled(True)  # Включаем виджеты, если объект выбран
        else:
            self.model.update_data(None)  # Очищаем таблицу, если объект не выбран
            self.set_widgets_enabled(False)  # Отключаем виджеты, если объект не выбран

    def set_widgets_enabled(self, enabled):
        """Включает или отключает виджеты в зависимости от флага enabled."""
        self.table_view.setEnabled(enabled)
        self.add_button.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)

    def add_related_object(self):
        """Добавление пустого объекта в таблицу."""
        if not self.related_description or not self.current_object:
            return

        # Добавляем пустую строку
        self.model.add_empty_row()

    def get_selected_object(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if selected_indexes:
            selected_row = selected_indexes[0].row()
            return self.model.data_rows[selected_row]
        return None

    def remove_related_object(self):
        selected_object = self.get_selected_object()
        if selected_object:
            getattr(self.current_object, self.related_description.attribute).remove(selected_object)
            self.session.commit()
            self.update_table(self.current_object)

