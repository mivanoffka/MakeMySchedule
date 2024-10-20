from enum import Enum


class ObservableTaskResultStatus(Enum):
    SUCCESS = 0,
    FAILED = 1,
    PARTIAL = 2
