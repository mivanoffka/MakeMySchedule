from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView, QHeaderView, QGroupBox, QHBoxLayout, \
    QPushButton, QComboBox, QLabel

from ....data import ForeignKeyColumnDescription
from .delegate import ForeignKeyDelegate
from .model import PrimaryTableModel

class PrimaryTableWidget(QWidget):
    selection_changed = Signal(object)

    def __init__(self, session, orm_class, visible_columns, table_title, parent=None):
        super().__init__(parent)
        self.session = session
        self.orm_class = orm_class

        self.visible_columns = []
        self.filter_columns = []
        for column in visible_columns:
            if isinstance(column, ForeignKeyColumnDescription):
                if column.as_filter:
                    self.filter_columns.append(column)
            self.visible_columns.append(column)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.table_view = QTableView()
        self.table_view.verticalHeader().setDefaultSectionSize(20)
        self.model = PrimaryTableModel(self.session, self.orm_class, self.visible_columns)
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table_group_box = QGroupBox(table_title)
        self.table_group_box.setLayout(QVBoxLayout())
        self.table_group_box.layout().addWidget(self.table_view)

        self.layout.addWidget(self.table_group_box)

        self._add_remove_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.add_button.clicked.connect(self.add_record)
        self.delete_button.clicked.connect(self.delete_record)
        self._add_remove_layout.addWidget(self.add_button)
        self._add_remove_layout.addWidget(self.delete_button)
        self.table_group_box.layout().addLayout(self._add_remove_layout)
        self.table_group_box.layout().setSpacing(0)
        self._add_remove_layout.setSpacing(4)
        self.table_view.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self.layout.setContentsMargins(0, 0, 0, 0)

        for i, column in enumerate(self.visible_columns):
            if isinstance(column, ForeignKeyColumnDescription):
                delegate = ForeignKeyDelegate(self.table_view, self.session, column)
                self.table_view.setItemDelegateForColumn(i, delegate)

            if column in self.filter_columns:
                self.table_view.setColumnHidden(i, True)
        self.filter_widgets = {}

        self.filters_layout = QHBoxLayout()
        if self.filter_columns:
            self.layout.addLayout(self.filters_layout)
        self.filters_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        for column in self.filter_columns:
            combo_box_layout = QHBoxLayout()
            label = QLabel(column.displayed_name)
            combo_box_layout.addWidget(label, 1)
            combo_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

            combo_box = QComboBox()
            combo_box.addItems(self._get_unique_values(column))
            combo_box.addItem("(Не выбрано)")

            combo_box_layout.addWidget(combo_box, 2)

            combo_box.currentTextChanged.connect(self.filter)
            self.filters_layout.addLayout(combo_box_layout)
            self.filter_widgets[column] = combo_box

        self.filter()

    def filter(self):
        filter = dict.fromkeys(self.filter_columns, None)
        for column in self.filter_columns:
            filter[column] = self.filter_widgets[column].currentText()

        self.model.filter_data(filter)

    def _get_unique_values(self, column):
        query = self.session.query(column.orm_type).distinct().all()
        return tuple(column.represent(obj) for obj in query)

    def filter_data(self, column, selected_value):
        if selected_value == "Все":
            self.model.reset_data()
        elif selected_value == "(Не выбрано)":
            self.model.filter_data(column, None)
        else:
            self.model.filter_data(column, selected_value)

    def _on_selection_changed(self):
        selected_object = self._get_selected_object()
        self.selection_changed.emit(selected_object)

    def _get_selected_object(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if selected_indexes:
            selected_row = selected_indexes[0].row()
            return self.model.data_rows[selected_row]
        return None

    def add_record(self):
        new_record = self.orm_class()

        for column in self.filter_columns:
            filter_value = self.filter_widgets[column].currentText()

            if filter_value not in ["(Все)", "(Не выбрано)"]:

                objs = self.session.query(column.orm_type).all()
                filtered_objs = [obj for obj in objs if column.represent(obj) == filter_value]
                if filtered_objs:
                    selected_obj = filtered_objs[0]
                    setattr(new_record, column.attribute, selected_obj.id)

        self.session.add(new_record)
        self.session.commit()

        self.model.refresh()
        self.filter()

    def delete_record(self):
        selected_object = self._get_selected_object()
        if selected_object:
            self.session.delete(selected_object)
            self.session.commit()
            self.model.refresh()

        self.filter()

    def has_empty_rows(self):
        for row in range(self.model.rowCount()):
            is_empty = True
            for column in range(self.model.columnCount()):
                # Получаем значение ячейки
                index = self.model.index(row, column)
                data = self.model.data(index, Qt.DisplayRole)
                if data and not data.strip() == "":
                    is_empty = False
                    break
            if is_empty:
                return True
        return False
