import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from config import BASE_DIR as PATH

# from utility import Singleton

SQL_LITE_PATH_TEMPLATE = 'sqlite:///{}'
RELATIVE_DB_PATH = "{}.db"


class SillyDB:
    __engine: Engine
    __session_maker: sessionmaker
    __name: str

    def get_session(self):
        return self.__session_maker()

    def __init__(self, name, declarative_base):
        self.__name = name
        self.__engine = create_engine(SQL_LITE_PATH_TEMPLATE.format(RELATIVE_DB_PATH.format(name)))
        declarative_base.metadata.create_all(self.__engine)
        self.__session_maker = sessionmaker(bind=self.__engine)
