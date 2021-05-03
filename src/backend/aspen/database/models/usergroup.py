from __future__ import annotations

from collections import MutableSequence
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from aspen.database.models.base import idbase
from aspen.database.models.mixins import DictMixin

if TYPE_CHECKING:
    from aspen.database.models.cansee import CanSee


class Group(idbase, DictMixin):  # type: ignore
    """A group of users, generally a department of public health."""

    __tablename__ = "groups"

    name = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=True)

    can_see: MutableSequence[CanSee]
    can_be_seen_by: MutableSequence[CanSee]

    def __repr__(self):
        return f"Group <{self.name}>"


class User(idbase, DictMixin):  # type: ignore
    """A user."""

    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    auth0_user_id = Column(String, unique=True, nullable=False)
    group_admin = Column(Boolean, nullable=False)
    system_admin = Column(Boolean, nullable=False)
    agreed_to_tos = Column(Boolean, nullable=False, default=False)

    group_id = Column(Integer, ForeignKey(Group.id), nullable=False)
    group = relationship(Group, backref=backref("users", uselist=True))  # type: ignore

    def __repr__(self):
        return f"User <{self.name}>"
