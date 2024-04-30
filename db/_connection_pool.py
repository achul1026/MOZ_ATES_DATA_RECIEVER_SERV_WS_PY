import atexit
import json
import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from _logger import logger

with open('settings.json') as conf_j:
    config = json.load(conf_j)
db_config = config['db']


class DBPool:
    __instance = None
    pool_size = 5
    connect_args = {
        'raise_on_warnings': True,
        'failover': db_config["failover"]
    }

    @staticmethod
    def get_instance() -> 'DBPool':
        if DBPool.__instance is None:
            DBPool()
        return DBPool.__instance

    def __init__(self):
        if DBPool.__instance is not None:
            raise Exception("This class is a singleton.")
        else:
            # mysql uri (mysql://username:password@localhost/database_name)
            db_uri = f'mysql+mysqlconnector://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}'
            # generate engine with 10 pool size
            logger.info(f"DB Connection Pool {self.pool_size}")
            self.engine = create_engine(db_uri,connect_args=DBPool.connect_args, pool_size=self.pool_size,max_overflow=self.pool_size)

            # generate session
            logger.info("Generate session Start")
            self.session_maker = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_maker)
            logger.info("Generate session End")

            DBPool.__instance = self
            atexit.register(DBPool.close_all)

    @staticmethod
    def get_session() -> Session:
        return DBPool.get_instance().Session

    @staticmethod
    def close_all():
        print("close sessions")
        DBPool.get_instance().Session.close_all()

