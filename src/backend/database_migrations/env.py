import os
from logging.config import fileConfig
from typing import Mapping, Type

import enumtables  # noqa: F401
from alembic import context
from sqlalchemy import create_engine

from aspen.config.config import Config
from aspen.config.docker_compose import DockerComposeConfig
from aspen.database.connection import get_db_uri
from aspen.database.models import meta

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)


target_metadata = [meta]


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_uri():
    if "DB" in os.environ:
        db_env = os.environ["DB"]
    else:
        # TODO: generate the appropriate list of "RuntimeEnvironment"s from the enum.
        raise ValueError(
            "Must provide env variable DB=[docker, local, remote, dev, staging, prod]"
        )

    config_mapper: Mapping[str, Type[Config]] = {
        "docker": DockerComposeConfig,
        "local": Config,
        "remote": Config,
    }
    return get_db_uri(config_mapper[db_env]())


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=get_uri(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(get_uri())

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
