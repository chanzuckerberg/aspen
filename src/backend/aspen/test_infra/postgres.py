import random
import string
from dataclasses import dataclass
from typing import Generator

import pytest

from aspen.database import connection as aspen_connection

USERNAME = "user_rw"
PASSWORD = "password_rw"
INITIAL_DATABASE = "postgres"


@dataclass
class PostgresDatabase:
    database_name: str
    port: int

    def as_uri(self):
        return f"postgresql://{USERNAME}:{PASSWORD}@database:{self.port}/{self.database_name}"


@pytest.fixture()
def postgres_database() -> Generator[PostgresDatabase, None, None]:
    """Creates a postgres test database named a random string with username/password user_rw/password_rw, yields it, and then drops it."""

    # create admin sql connection to create test database
    admin_uri = "postgresql://postgres:password_postgres@database:5432/aspen_db"
    admin_sql_interface = aspen_connection.init_db(admin_uri)
    admin_session = admin_sql_interface.make_session()
    # set isolation level to allow admin to create db
    admin_session.connection().connection.set_isolation_level(0)

    # create random database name (for running tests in parallel)
    letters = string.ascii_lowercase
    database_name = "".join(random.choice(letters) for i in range(10))

    admin_session.execute(f"create database {database_name}")
    admin_session.execute(
        f"grant all privileges on database {database_name} to {USERNAME}"
    )

    postgres_test_db = PostgresDatabase(database_name=database_name, port=5432)

    yield postgres_test_db

    admin_session.execute(f"drop database {database_name} with (force)")
