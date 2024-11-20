from PySide6.QtWidgets import QHBoxLayout, QWidget, QMainWindow

from application.data.orm import Lesson
from application.windows.editor.schedule_table.day_widget import ScheduleDayWidget
from application.windows.editor.schedule_table.table_widget import ScheduleTableWidget

from ...data import TableDescription, ListColumnDescription
from .related_table import RelatedTableWidget
from .primary_table import PrimaryTableWidget
from .. import MessageWindow


class EditorWindow(QMainWindow):
    _table_description: TableDescription
    _related_description: ListColumnDescription = None

    def __init__(self, data, session, orm_class):
        super().__init__()
        self.session = session
        self.data = data
        self.orm_class = orm_class
        self._related_descriptions = None

        if orm_class in self.data.table_descriptions:
            self._table_description = self.data.table_descriptions[orm_class]
            if self._table_description.list_columns():
                self._related_descriptions = []
                for desc in self._table_description.list_columns():
                    self._related_descriptions.append(desc)

        self._main_widget = QWidget(self)
        self.setCentralWidget(self._main_widget)
        self._main_layout = QHBoxLayout()
        self._main_widget.setLayout(self._main_layout)

        self.visible_columns = self._table_description.regular_columns()

        if orm_class != Lesson:
            self.primary_table_widget = PrimaryTableWidget(
                session=self.session,
                orm_class=self.orm_class,
                visible_columns=self.visible_columns,
                table_title=self._table_description.displayed_name
            )
        else:
            self.primary_table_widget = ScheduleTableWidget(
                session=self.session,
                orm_class=self.orm_class,
                visible_columns=self.visible_columns,
                table_title=self._table_description.displayed_name
            )
            
        self._main_layout.addWidget(self.primary_table_widget, 2)

        self.related_widgets = []
        if self._related_descriptions:
            for desc in self._related_descriptions:
                widget = RelatedTableWidget(
                    session=self.session,
                    related_description=desc
                )
                self._main_layout.addWidget(widget, 1)
                self.primary_table_widget.selection_changed.connect(widget.update_table)
                self.related_widgets.append(widget)

    def closeEvent(self, event):

        """Переопределяем событие закрытия окна."""
        if self.primary_table_widget.has_empty_rows():
            # Выводим предупреждение пользователю
            MessageWindow.show_warning("Прежде чем выйти, заполните пустые строки, либо удалите их.")

            # Блокируем закрытие окна
            event.ignore()
        else:
            # Разрешаем закрытие окна
            event.accept()
