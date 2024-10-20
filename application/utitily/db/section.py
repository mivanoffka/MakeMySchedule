from .db import SillyDB


class SillyDbSection:
    __db: SillyDB

    def _get_session(self):
        return self.__db._get_session()

    def __init__(self, db: SillyDB):
        self.__db = db
