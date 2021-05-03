import alembic.autogenerate
from alembic.autogenerate.render import _ident
from sqlalchemy import MetaData

from . import enum_column
from . import alembic_ops


def _get_fk_table_name(column):
    for fk in column.foreign_keys:
        colspec = fk._get_colspec()
        # the colspec is either in the form tablename.columnname or
        # schemaname.tablename.columnname.
        splitted = colspec.split(".")
        assert len(splitted) >= 2
        tablename = splitted[-2]
        return tablename


def get_declared_enums(metadatas, schema, default):
    enum_columns = [
        (column, _get_fk_table_name(column))
        for metadata in metadatas
        for table in metadata.tables.values()
        for column in table.columns
        if (isinstance(column.type, enum_column.EnumType) and table.schema == schema)
    ]

    return {
        tablename: frozenset(member._value_ for member in column.type.__enum__)
        for column, tablename in enum_columns
    }


@alembic.autogenerate.comparators.dispatch_for("schema")
def compare_enums(autogen_context, upgrade_ops, schema_names):
    known_tables = get_connection_tables(autogen_context, schema_names)

    for schema in schema_names:
        default = autogen_context.dialect.default_schema_name
        if schema is None:
            schema = default

        # autogen_context.metadata can be a single MetaData instance or a sequence of
        # them.  Normalize it so that it's always a sequence.
        if isinstance(autogen_context.metadata, MetaData):
            metadatas = (autogen_context.metadata,)
        else:
            metadatas = autogen_context.metadata
        enums = get_declared_enums(metadatas, schema, default)
        for table, values in enums.items():
            if (schema, table) in known_tables:
                items = {
                    r[0]
                    for r in autogen_context.connection.execute(
                        f"SELECT {_ident('item_id')} FROM {_ident(schema)}.{_ident(table)}"
                    )
                }
                to_add = values - items
                to_remove = items - values
                if to_add:
                    upgrade_ops.ops.append(
                        alembic_ops.EnumInsertOp(schema, table, list(to_add))
                    )
                if to_remove:
                    upgrade_ops.ops.append(
                        alembic_ops.EnumDeleteOp(schema, table, list(to_remove))
                    )
            else:
                upgrade_ops.ops.append(
                    alembic_ops.EnumInsertOp(schema, table, list(values))
                )


def get_connection_tables(autogen_context, schema_names):
    """
    Returns a sequence of (schema, tables) tuples that reflects the current state of the
    database.

    This is inspired by the code in alembic.autogenerate._autogen_for_tables
    and alembic.autogenerate._compare_tables.
    """
    inspector = autogen_context.inspector
    default_schema_name = autogen_context.dialect.default_schema_name

    conn_table_names = set()

    version_table_schema = autogen_context.migration_context.version_table_schema
    version_table = autogen_context.migration_context.version_table

    for schema_name in schema_names:
        if schema_name is None:
            schema_name = default_schema_name
        tables = set(inspector.get_table_names(schema=schema_name))
        if schema_name == version_table_schema:
            tables = tables.difference(
                [autogen_context.migration_context.version_table]
            )

        conn_table_names.update(
            (schema_name, tname)
            for tname in tables
            if autogen_context.run_name_filters(
                tname, "table", {"schema_name": schema_name}
            )
        )

    return conn_table_names
