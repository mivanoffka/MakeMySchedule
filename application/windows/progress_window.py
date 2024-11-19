from datetime import timedelta
from typing import Optional, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QWidget, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                               QLabel, QProgressBar, QTextEdit)


from PySide6.QtCore import QThread
from .widget_for_showing_progress import IWidgetForShowingProgress
from .background_task import BackgroundTask
from ..logic import ObservableTask


class ProgressWindow(QDialog, IWidgetForShowingProgress):
    __task: ObservableTask
    __finding_result: Optional[list] = None
    __execution_result: Any = None
    __duration: timedelta

    @property
    def duration(self):
        return self.__duration

    @property
    def execution_result(self) -> Any:
        return self.__execution_result

    @property
    def task_thread(self) -> QThread:
        return self.__task_thread

    @property
    def progress_thread(self) -> QThread:
        return self.__progress_thread

    def on_task_finish(self, result: Any):
        self.__execution_result = result[0]
        self.__duration = result[1]
        # self.close()

    def __init__(self, parent, task: ObservableTask):
        super().__init__(parent=parent)

        self.__task = task

        self.__main_widget = QWidget()
        self.__main_layout = QVBoxLayout()
        self.__main_layout.setSpacing(8)
        self.setLayout(self.__main_layout)

        self.__text_box = QTextEdit()
        self.__main_layout.addWidget(self.__text_box)

        self.__progress_bar = QProgressBar()
        self.__progress_bar.setTextVisible(False)
        self.__progress_bar.setRange(0, 100)
        self.__percentage_label = QLabel("0%")
        self.__percentage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.__main_layout.addWidget(self.__progress_bar)
        self.__main_layout.addWidget(self.__percentage_label)

        self.setWindowTitle("Выполняется составление расписания...")
        self.setFixedSize(400, 300)

        self.__setup()

    def __setup(self):
        self.__task_thread = QThread()
        self.__progress_thread = QThread()

        task_worker = BackgroundTask(self.__task, self)
        task_worker.start()

    def update_progress(self, percentage):
        self.__percentage_label.setText(f"{percentage}%")
        self.__progress_bar.setValue(int(percentage))

    def update_output(self, message):
        self.__text_box.append(message)

    def display_result(self, result):
        self.__progress_bar.setValue(100)
