import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from config import BASE_DIR as PATH

# from utility import Singleton

SQL_LITE_PATH_TEMPLATE = "sqlite:///{}"
RELATIVE_DB_PATH = "{}.db"


class SillyDB:
    __engine: Engine
    __session_maker: sessionmaker
    _path: Optional[str] = None

    def get_session(self):
        return self.__session_maker()

    def set_source(self):
        self.__engine = create_engine(SQL_LITE_PATH_TEMPLATE.format(self._path))
        self.__declarative_base.metadata.create_all(self.__engine)
        self.__session_maker = sessionmaker(bind=self.__engine)

    def __init__(self, declarative_base):
        self.__declarative_base = declarative_base
