# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The database connection.
"""


from dataclasses import dataclass
from typing import Type

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from .config import get_settings


class SBase(DeclarativeBase):
    """The source database base data model."""


@dataclass
class URLSessionMakerCache:
    """The cache of the SQLAlchemy database URL and its session maker."""

    url: str
    """The SQLAlchemy database URL."""
    session_local: sessionmaker
    """The session maker."""


class DataSource:
    """The data source."""

    def __init__(self):
        self.__cache: dict[str, URLSessionMakerCache] = {}
        """The cache of the SQLAlchemy database URL and its session maker."""

    def get_db(self, env: str = "dev") -> Session:
        """Connects and returns a session based on the environment.

        :param env: "dev", "test"
        :return: The database session.
        """
        if env == "test":
            url = get_settings().SQLALCHEMY_TEST_DATABASE_URL
        else:
            url = get_settings().SQLALCHEMY_SOURCE_DATABASE_URL

        session_local = self.__get_db_sessionmaker(url, SBase)
        return session_local()

    def __get_db_sessionmaker(
        self, url: str, base: Type[DeclarativeBase]
    ) -> sessionmaker:
        """Connects and returns a database sessionmaker.

        :param url: The SQLAlchemy database URL.
        :param base: The base data model.
        :return: The database sessionmaker.
        """
        if url not in self.__cache:
            engine: sa.Engine = sa.create_engine(url)
            base.metadata.bind = engine
            session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.__cache[url] = URLSessionMakerCache(
                url=url, session_local=session_local
            )
        return self.__cache[url].session_local

    def clear_cache(self) -> None:
        """Cleans-up the cache sessionmaker."""
        self.__cache.clear()


ds: DataSource = DataSource()
"""The data source."""
