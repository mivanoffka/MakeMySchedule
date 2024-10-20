import ctypes
import platform
import subprocess
import sys
import threading
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from config import BASE_DIR
from .utitily import SillyLogger as Logger
from .data import Data
from .windows import MainWindow, MessageWindow

import logging

class Application:
    __app: QApplication
    __main_window: MainWindow
    __logger: Logger
    __data: Data

    def start(self):
        self.__data = Data("curriculum")
        self.__app = QApplication(sys.argv)
        self.__main_window = MainWindow(self.__data)

        self.__logger = Logger("logs")

        try:
            self.__main_window.show()
            self.__app.exec()
        except Exception as error:
            MessageWindow.show_error("Произошла критическая ошибка!", )


