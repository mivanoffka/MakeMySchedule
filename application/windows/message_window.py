from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import *

from .enums import MessageResult, MessageType

class MessageWindow(QDialog):

    """
    A custom MessageBox instead of qt-builtins that are platform-dependent.

    Instances of this class are advised to not be created manually,
    you better create templated message-windows using the class' static methods
    """

    windows_container = []
    _message_result: Optional[MessageResult] = None

    @property
    def message_result(self):
        return self._message_result

    def __init__(self, message, title="Сообщение", icon_emoji: str = "ℹ️", action_on_closed=None, message_type: MessageType = MessageType.OK):
        super().__init__()

        self.__main_widget = QWidget()
        self.__main_widget.setContentsMargins(0, 0, 0, 0)
        self.__main_layout = QVBoxLayout()
        self.__main_layout.setSpacing(4)
        self.__main_widget.setLayout(self.__main_layout)
        self.setLayout(self.__main_layout)

        self.__icon_and_message_layout = QHBoxLayout()
        self.__main_layout.addLayout(self.__icon_and_message_layout)

        self.__icon_label = QLabel(icon_emoji)
        self.__icon_label.setStyleSheet("font-size: 48px;")
        self.__icon_and_message_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__icon_and_message_layout.addWidget(self.__icon_label, 1)

        self.__message_label = QLabel(message)
        self.__message_label.setWordWrap(True)
        self.__icon_and_message_layout.addWidget(self.__message_label, 6)

        self.__buttons_layout = QHBoxLayout()
        self.__buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.__buttons_layout.setSpacing(0)
        self.__main_layout.addLayout(self.__buttons_layout)
        self._init_buttons(message_type)

        height_delta = 24
        line_len = 32
        height = height_delta * len(message) // line_len
        self.__message_label.setFixedHeight(height)
        self.setFixedWidth(320)
        self.setWindowTitle(title)

        self.finished.connect(action_on_closed)

    def _init_buttons(self, message_type: MessageType):
        match message_type:
            case MessageType.OK:
                self.__ok_button = QPushButton("OK")
                self.__ok_button.clicked.connect(self.on_ok_button_clicked)
                self.__buttons_layout.addWidget(self.__ok_button)
            case MessageType.YesNo:
                self.__yes_button = QPushButton("Да")
                self.__buttons_layout.addWidget(self.__yes_button)
                self.__yes_button.clicked.connect(self.on_yes_button_clicked)
                self.__no_button = QPushButton("Нет")
                self.__buttons_layout.addWidget(self.__no_button)
                self.__no_button.clicked.connect(self.on_no_button_clicked)

    def on_ok_button_clicked(self):
        self._result = MessageResult.OK
        self.close()

    def on_yes_button_clicked(self):
        print("ye")
        self._message_result = MessageResult.YES
        self.close()

    def on_no_button_clicked(self):
        self._message_result = MessageResult.NO
        self.close()

    @staticmethod
    def show_confirmation(message, title="Вопрос", icon_emoji="❓", action_on_closed=None):
        message_window = MessageWindow(message, title, icon_emoji, action_on_closed, message_type=MessageType.YesNo)
        MessageWindow.windows_container.append(message_window)
        message_window.exec()

        return message_window.message_result

    @staticmethod
    def show_informative(message, title="Сообщение", icon_emoji="ℹ️", action_on_closed=None):
        message_window = MessageWindow(message, title, icon_emoji, action_on_closed)
        MessageWindow.windows_container.append(message_window)
        message_window.exec()

        return message_window

    @staticmethod
    def show_error(message):
        message_window = MessageWindow(message, title="Ошибка", icon_emoji="❌")
        MessageWindow.windows_container.append(message_window)
        message_window.show()

        return message_window

    @staticmethod
    def show_warning(message):
        message_window = MessageWindow(message, title="Внимание!", icon_emoji="⚠️")
        MessageWindow.windows_container.append(message_window)
        message_window.show()

        return message_window

