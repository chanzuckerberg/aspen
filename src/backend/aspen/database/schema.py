import sqlalchemy.event as sqlalchemy_event
from sqlalchemy import DDL

from aspen.database.connection import session_scope, SqlAlchemyInterface
from aspen.database.models import meta


def create_tables_and_schema(interface: SqlAlchemyInterface):
    """Creates the schema and all tables"""
    with session_scope(interface) as session:
        sqlalchemy_event.listen(
            meta,
            "before_create",
            DDL(f"CREATE SCHEMA IF NOT EXISTS {meta.schema}"),
        )
        meta.create_all(bind=interface.engine)
        reset_permissions(session, meta.schema)


def reset_permissions(session, schema):
    """This function renews the read permissions for the read-only user"""
    for statement in (
        f"GRANT USAGE ON SCHEMA {schema} TO user_ro",
        f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO user_ro",
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} GRANT SELECT ON TABLES TO user_ro",
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} GRANT SELECT ON SEQUENCES TO user_ro",
    ):
        session.execute(statement)
