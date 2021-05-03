import sqlalchemy.types as types
import sqlalchemy as sa

__all__ = ["EnumType"]


def convert_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class EnumType(types.TypeDecorator):
    impl = types.String

    def __init__(self, python_enum_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__enum__ = python_enum_type

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value._value_

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.__enum__(value)
