from __future__ import annotations

# the main models in the database
import enum

import enumtables
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from aspen.database.models.base import base, idbase
from aspen.database.models.enum import Enum
from aspen.database.models.usergroup import Group


class DataType(enum.Enum):
    TREES = "TREES"
    SEQUENCES = "SEQUENCES"
    METADATA = "METADATA"
    PRIVATE_IDENTIFIERS = "PRIVATE_IDENTIFIERS"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_DataTypeTable = enumtables.EnumTable(
    DataType,
    base,
    tablename="data_types",
)


class CanSee(idbase):  # type: ignore
    """
    Expresses a relationship where users from a group can see some data of another
    group.
    """

    __tablename__ = "can_see"

    viewer_group_id = Column(Integer, ForeignKey(Group.id), nullable=False)
    viewer_group = relationship(  # type: ignore
        Group, backref=backref("can_see", uselist=True), foreign_keys=[viewer_group_id]
    )
    owner_group_id = Column(Integer, ForeignKey(Group.id), nullable=False)
    owner_group = relationship(  # type: ignore
        Group,
        backref=backref("can_be_seen_by", uselist=True),
        foreign_keys=[owner_group_id],
    )
    data_type = Column(
        Enum(DataType),
        ForeignKey(_DataTypeTable.item_id),
        nullable=False,
    )
