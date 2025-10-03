from pydoc import text
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QMainWindow,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QLineEdit,
)

from ..data import Teacher, SubjectPartition, Data
from .editor import EditorWindow
from ..data import (
    Curriculum,
    ScheduledSubject,
    Room,
    RoomGroup,
    Group,
    Lesson,
    SubjectTitle,
)
from .message_window import MessageWindow
from ..logic import ComposerTask
from .progress_window import ProgressWindow


class MainWindow(QMainWindow):
    _data: Data

    def __init__(self, data: Data):
        super().__init__()
        self._data = data
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        self.buttons = []

        self.data_group_box_layout = QVBoxLayout()
        self.data_group_box_layout.setSpacing(2)

        self.main_layout.addLayout(self.data_group_box_layout)
        self.file_name = QLineEdit()
        self.file_name.setEnabled(False)
        # self.file_name.setFixedWidth(200)
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(2)
        self.open_db_button = QPushButton("Открыть")
        self.close_button = QPushButton("Закрыть")
        self.new_button = QPushButton("Новый")
        self.open_db_button.clicked.connect(self._open_file_dialog)
        self.new_button.clicked.connect(self._create_new_file)

        self.data_group_box_layout.addWidget(self.file_name, 3)
        self.data_group_box_layout.addLayout(self.buttons_layout, 1)

        self.buttons_layout.addWidget(self.open_db_button)
        self.buttons_layout.addWidget(self.close_button)
        self.buttons_layout.addWidget(self.new_button)

        columns_layout = QHBoxLayout()
        self.main_layout.addLayout(columns_layout)

        columns = (
            {
                "Аудитории": {
                    Room: "Перечень",
                    RoomGroup: "Категории",
                },
                "Учебные планы": {
                    Curriculum: "Перечень",
                    ScheduledSubject: "Заполнение",
                    Group: "Группы",
                },
            },
            {
                "Дисциплины и преподаватели": {
                    Teacher: "Преподаватели",
                    SubjectTitle: "Названия предметов",
                    SubjectPartition: "Разделение",
                },
                "Расписание": {Lesson: "Посмотреть", 1: "Составить"},
            },
        )

        values_dict = {
            "Популяция": 20,
            "Количество поколений": 100,
            "Вероятность мутации, %": 10,
        }

        self.values_group_box = QGroupBox("Параметры алгоритма")
        self.values_layout = QVBoxLayout()
        self.values_group_box.setLayout(self.values_layout)

        self.text_boxes = []

        for key, value in values_dict.items():
            line = QHBoxLayout()
            line.addWidget(QLabel(key), 1)
            box = QLineEdit(str(value))
            self.buttons.append(box)
            line.addWidget(box, 1)
            self.text_boxes.append(box)
            self.values_layout.addLayout(line)

        self.main_layout.addWidget(self.values_group_box)

        self.run_composer_button = QPushButton("Составить расписание")
        self.run_composer_button.clicked.connect(self._on_run_composer_button_clicked)
        self.buttons.append(self.run_composer_button)
        self.values_layout.addWidget(self.run_composer_button)

        for column in columns:
            column_widget = QVBoxLayout()
            columns_layout.addLayout(column_widget)
            for group_box in column.keys():
                group_box_widget = QGroupBox(group_box)
                group_box_layout = QVBoxLayout()
                group_box_layout.setSpacing(2)
                group_box_widget.setLayout(group_box_layout)

                for orm_class in column[group_box].keys():
                    if orm_class == 1:
                        ...
                    else:
                        button = QPushButton(column[group_box][orm_class])
                        button.clicked.connect(
                            lambda _, k=orm_class: self._show_orm_window(k)
                        )
                        self.buttons.append(button)
                        group_box_layout.addWidget(button)

                column_widget.addWidget(group_box_widget)

        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Составитель расписаний")
        self._refresh_label()

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "*.db")
        if file_path:
            self._data.path = file_path
        self._refresh_label()

    def _create_new_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Создать новый файл", "", "База данных (*.db)"
        )
        if file_path:
            try:
                # Создаем пустой файл .db
                with open(file_path, "w") as db_file:
                    pass
                self._data.path = file_path
                self._refresh_label()
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось создать файл: {str(e)}"
                )

    def _refresh_label(self):
        if self._data.path:
            self.file_name.setText(self._data.path)
            for button in self.buttons:
                button.setEnabled(True)
        else:
            self.file_name.setText("[ Файл не открыт ]")
            for button in self.buttons:
                button.setEnabled(False)

    def _on_run_composer_button_clicked(self):
        values = []
        for box in self.text_boxes:
            box: QLineEdit = box
            values.append(float(box.text().replace(",", ".")))

        values[2] = values[2] / 100
        print(values)

        task = ComposerTask(self._data, *values)
        self._progress_window = ProgressWindow(self, task)
        self._progress_window.on_task_finish
        self._progress_window.show()

    def _show_orm_window(self, orm_class):
        self.orm_window = EditorWindow(self._data, self._data.get_session(), orm_class)
        self.orm_window.show()
