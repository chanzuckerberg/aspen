
import alembic.autogenerate.render
from alembic.operations import Operations, MigrateOperation
from sqlalchemy import text

__all__ = ["EnumInsertOp", "EnumDeleteOp"]

@Operations.register_operation("enum_insert")
class EnumInsertOp(MigrateOperation):

	def __init__(self, schema, tablename, data = []):
		self.schema = schema
		self.tablename = tablename
		self.data = data

	@classmethod
	def enum_insert(cls, operations, tablename, data = [], schema=None):
		op = cls(schema, tablename, data)
		return operations.invoke(op)

	def reverse(self):
		return EnumDeleteOp(self.schema, self.tablename, self.data)

	@property
	def fully_qualified_tablename(self):
		return "%s.%s" % (self.schema, self.tablename) if self.schema else self.tablename


@Operations.register_operation("enum_delete")
class EnumDeleteOp(MigrateOperation):

	def __init__(self, schema, tablename, data = []):
		self.schema = schema
		self.tablename = tablename
		self.data = data

	@classmethod
	def enum_delete(cls, operations, tablename, data = [], schema=None):
		op = cls(schema, tablename, data)
		return operations.invoke(op)

	def reverse(self):
		return EnumInsertOp(self.tablename, self.data)

	@property
	def fully_qualified_tablename(self):
		return "%s.%s" % (self.schema, self.tablename) if self.schema else self.tablename

@Operations.implementation_for(EnumInsertOp)
def insert(operations, operation):
	if not operation.data:
		return

	for value in operation.data:
		operations.execute(
			text(f'INSERT INTO {alembic.autogenerate.render._ident(operation.fully_qualified_tablename)} ({alembic.autogenerate.render._ident("item_id")}) VALUES (:vl)').params({"vl": value}))

@Operations.implementation_for(EnumDeleteOp)
def delete(operations, operation):
	if not operation.data:
		return
	operations.execute(
		text(f'DELETE FROM {alembic.autogenerate.render._ident(operation.fully_qualified_tablename)} WHERE {alembic.autogenerate.render._ident("item_id")} IN :vl').params({"vl": tuple(operation.data)})
	)

@alembic.autogenerate.render.renderers.dispatch_for(EnumInsertOp)
def render_sync_enum_value_op(autogen_context, op):
	return 'op.enum_insert("{}", {!r}, schema={!r})'.format(op.tablename, op.data, op.schema)

@alembic.autogenerate.render.renderers.dispatch_for(EnumDeleteOp)
def render_sync_enum_value_op(autogen_context, op):
	return 'op.enum_delete("{}", {!r}, schema={!r})'.format(op.tablename, op.data, op.schema)
