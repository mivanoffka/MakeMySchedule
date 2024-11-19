from abc import ABCMeta, abstractmethod
from typing import Any

from PySide6.QtCore import QThread


class IWidgetForShowingProgress:
    @abstractmethod
    def update_progress(self, progress_value):
        raise NotImplementedError()

    @abstractmethod
    def update_output(self, message):
        raise NotImplementedError()

    @property
    @abstractmethod
    def task_thread(self) -> QThread:
        raise NotImplementedError()

    @property
    @abstractmethod
    def progress_thread(self) -> QThread:
        raise NotImplementedError()

    @abstractmethod
    def on_task_finish(self, result: Any):
        raise NotImplementedError()
