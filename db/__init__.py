import logging

from sqlalchemy.orm import Session

from db._connection_pool import DBPool
from db._models import *

instance = DBPool.get_instance()


def open_session() -> Session:
    return instance.Session()