import datetime
import enum

from sqlalchemy import Column, Integer

# a collection of mixin classes to help build the models


# everyone needs an auto-generated primary key
class BaseMixin:
    """Base model: all models have integer primary keys"""

    id = Column(Integer, primary_key=True, autoincrement=True)


class DictMixin:
    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            column_value = getattr(self, column.name)
            if isinstance(column_value, (datetime.datetime, datetime.date)):
                d[column.name] = column_value.isoformat()

            else:
                if isinstance(column_value, enum.Enum):
                    d[column.name] = column_value.value
                else:
                    d[column.name] = column_value

        return d
