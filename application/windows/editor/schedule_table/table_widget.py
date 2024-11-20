from calendar import Day
from PySide6.QtWidgets import QHBoxLayout, QWidget, QMainWindow
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView, QHeaderView, QGroupBox, QHBoxLayout, \
    QPushButton, QComboBox, QLabel

from application.data.orm import Group

from .day_widget import ScheduleDayWidget

titles = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

class ScheduleTableWidget(QWidget):
    def _get_unique_values(self):
        query = self.session.query(Group).distinct().all()
        return tuple(obj.name for obj in query)
    
    def switch_group(self):
        for widget in self.day_widgets:
            widget.set_group(self.group_combo_box.currentText())

    
    def __init__(self, session, orm_class, visible_columns, table_title, parent=None):
        super().__init__()
        self.session = session
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.group_layout = QHBoxLayout()
        self.group_combo_box = QComboBox()
        self.group_combo_box.addItems(self._get_unique_values())
        self.group_combo_box.currentTextChanged.connect(self.switch_group)
        self.group_layout.addWidget(self.group_combo_box)
        self.layout.addLayout(self.group_layout)

        self.day_widgets = []
        for i in range(0, 3):
            layout = QHBoxLayout()
            for j in range(0, 2):
                index = i * 2 + j
                widget = ScheduleDayWidget(index, session, orm_class, visible_columns, titles[index])
                
                layout.addWidget(widget)
                self.day_widgets.append(widget)
            self.layout.addLayout(layout)
    