import datetime

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session

from aspen.database.models.usergroup import User


def get_usergroup_query(session: Session, user_id: str) -> Query:
    return (
        session.query(User)
        .options(joinedload(User.group))
        .filter(User.auth0_user_id == user_id)
    )


def format_date(dt: datetime.date, format="%Y-%m-%d") -> str:
    return dt.strftime(format)


def format_datetime(dt: datetime.datetime, format="%Y-%m-%d %I:%M%p") -> str:
    return dt.strftime(format)
