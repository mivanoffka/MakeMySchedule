import logging
from abc import abstractmethod
from typing import Any, Tuple, List
from .task_result import ObservableTaskResult


class ObservableTask:
    """
    Base class for all long-lasting tasks. Such tasks are meant to be executed via INTERNAL SERVER.
    Using a PROGRESS TRACKER in class implementations is strictly advised. Otherwise, your task probably
    should not be an OBSERVABLE TASK.
    """

    __recent_messages: List[Any] = []
    __total_messages: List[Any] = []

    def make_message(self, message: Any):
        logging.warning(message)
        self.__recent_messages.append(message)
        self.__total_messages.append(message)

    @property
    def total_messages(self):
        return self.__total_messages

    @property
    def recent_messages(self) -> Tuple[Any, ...]:
        cpy = tuple(message for message in self.__recent_messages)
        self.__recent_messages.clear()
        return cpy

    @abstractmethod
    def execute(self) -> ObservableTaskResult:
        """
        This method must be an entry point for performing the required task and must return the result of it.
        """
        raise NotImplementedError()

    @abstractmethod
    def _initialize_progress_units(self):
        """
        Everything connected with setting up a PROGRESS TRACKER must be stored here.
        """
        raise NotImplementedError()