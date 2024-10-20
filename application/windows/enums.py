from enum import Enum


class MessageType(Enum):
    OK = 0,
    YesNo = 1


class MessageResult(Enum):
    OK = 0,
    YES = 1,
    NO = 2