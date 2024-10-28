from PySide6.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QMainWindow
)

from ..data import Teacher, SubjectPartition, Data
from .editor import EditorWindow
from ..data import Curriculum, ScheduledSubject, Room, RoomGroup, Group, Lesson, SubjectTitle


class MainWindow(QMainWindow):
    def __init__(self, data: Data):
        super().__init__()
        self._data = data
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        self.buttons = []

        buttons_dict = {Curriculum: "Перечень учебных планов",
                        Group: "Группы",
                        Teacher: "Преподаватели",
                        SubjectTitle: "Названия предметов",
                        SubjectPartition: "Разделение",
                        ScheduledSubject: "Заполнение учебных планов",
                        Room: "Перечень всех аудитории",
                        RoomGroup: "Категории аудиторий",
                        Lesson: "Расписание"
                        }

        for key in buttons_dict.keys():
            button = QPushButton(buttons_dict[key])
            button.clicked.connect(lambda _, k=key: self._show_orm_window(k))
            self.main_layout.addWidget(button)

        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Составитель расписаний")

    def _show_orm_window(self, orm_class):
        self.orm_window = EditorWindow(self._data, self._data.get_session(), orm_class)
        self.orm_window.show()

