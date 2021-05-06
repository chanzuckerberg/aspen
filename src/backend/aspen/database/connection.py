from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Generator, TYPE_CHECKING

from sqlalchemy import event
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from aspen.config.config import Config


class SqlAlchemyInterface:
    def __init__(self, engine: Engine):
        self._engine = engine
        self._session_maker = sessionmaker(bind=engine)

    @property
    def engine(self) -> Engine:
        return self._engine

    def make_session(self) -> Session:
        return self._session_maker()


def init_db(db_uri: str) -> SqlAlchemyInterface:
    engine = create_engine(db_uri)
    return SqlAlchemyInterface(engine)


@contextmanager
def session_scope(interface: SqlAlchemyInterface) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = interface.make_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_uri(runtime_config: Config, readonly: bool = False) -> str:
    """Provides a URI for the database based on a runtime environment.

    Parameters
    ----------
    runtime_config : Config
        The runtime config that contains the database we want to access.
    readonly : bool
        Returns a read-only handle for the database if True. (default: False)

    Returns
    -------
        string that can be used to connect to a postgres database
    """
    if readonly:
        try:
            return runtime_config.DATABASE_READONLY_URI
        except NotImplementedError:
            raise ValueError(f"Config {runtime_config} does not have a read-only mode.")
    return runtime_config.DATABASE_URI


sqltime_logger = logging.getLogger("sqltime")
sqltime_logger.setLevel(logging.DEBUG)


def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())
    sqltime_logger.debug("Start Query: %s", statement)


def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info["query_start_time"].pop(-1)
    sqltime_logger.debug("Query Complete!")
    sqltime_logger.debug("Total Time: %f", total)


def enable_profiling():
    event.listen(Engine, "before_cursor_execute", _before_cursor_execute)
    event.listen(Engine, "after_cursor_execute", _after_cursor_execute)


def disable_profiling():
    event.remove(Engine, "before_cursor_execute", _before_cursor_execute)
    event.remove(Engine, "after_cursor_execute", _after_cursor_execute)


@contextmanager
def enable_profiling_ctx():
    enable_profiling()
    yield
    disable_profiling()
