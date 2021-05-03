from typing import Type, TYPE_CHECKING, TypeVar

# https://github.com/dropbox/sqlalchemy-stubs/issues/114
# This is the (gross) workaround. Keep an eye on the issue and get rid of it once it's fixed.
if TYPE_CHECKING:
    from sqlalchemy.sql.type_api import TypeEngine

    T = TypeVar("T")

    class Enum(TypeEngine[T]):
        def __init__(self, enum: Type[T]) -> None:
            ...


else:
    from enumtables import EnumType as Enum  # noqa: F401
