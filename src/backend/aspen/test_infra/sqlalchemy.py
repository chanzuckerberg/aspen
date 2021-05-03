from typing import Generator

import pytest
from sqlalchemy.orm.session import Session

from aspen.database import connection as aspen_connection
from aspen.database import schema
from aspen.test_infra.postgres import PostgresDatabase


@pytest.fixture()
def sqlalchemy_interface(
    postgres_database: PostgresDatabase,
) -> Generator[aspen_connection.SqlAlchemyInterface, None, None]:
    """initialize schema and yield interface"""
    test_db_interface = aspen_connection.init_db(postgres_database.as_uri())
    schema.create_tables_and_schema(test_db_interface)
    connection = test_db_interface.engine.connect()
    yield test_db_interface
    connection.close()


@pytest.fixture()
def session(
    sqlalchemy_interface: aspen_connection.SqlAlchemyInterface,
) -> Generator[Session, None, None]:
    session = sqlalchemy_interface.make_session()
    yield session
    session.close()
