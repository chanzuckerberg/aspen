import json
import logging
from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping

from auth0.v3 import authentication as auth0_authentication
from auth0.v3 import management as auth0_management
from sqlalchemy import or_
from sqlalchemy.orm import configure_mappers, joinedload, Session

from aspen.config import config as aspen_config
from aspen.database.connection import session_scope, SqlAlchemyInterface
from aspen.database.models import Group, User
from covid_database import init_db as covidhub_init_db
from covid_database import SqlAlchemyInterface as CSqlAlchemyInterface
from covid_database import util as covidhub_database_util
from covid_database.models import covidtracker
from covid_database.models.ngs_sample_tracking import Project

logger = logging.getLogger(__name__)


@dataclass
class Auth0Entry:
    nickname: str
    email: str
    auth0_token: str


def covidhub_interface_from_secret(
    covidhub_aws_profile: str, secret_id: str
) -> CSqlAlchemyInterface:
    interface = covidhub_init_db(
        covidhub_database_util.get_db_uri(secret_id, aws_profile=covidhub_aws_profile)
    )
    return interface


def get_or_make_group(session: Session, name: str, address: str) -> Group:
    group = session.query(Group).filter(Group.name == name).one_or_none()
    if group is None:
        # copy the project info into the "group"
        group = Group(
            name=name,
            address=address,
        )
        session.add(group)

    return group


def import_project_users(
    interface: SqlAlchemyInterface,
    covidhub_aws_profile: str,
    covidhub_secret_id: str,
    rr_project_id: str,
    auth0_usermap: Mapping[str, Auth0Entry],
):
    configure_mappers()
    covidhub_interface = covidhub_interface_from_secret(
        covidhub_aws_profile, covidhub_secret_id
    )
    covidhub_session: Session = covidhub_interface.make_session()

    with session_scope(interface) as session:
        project = (
            covidhub_session.query(Project)
            .options(
                joinedload(
                    Project.covidtracker_group, covidtracker.GroupToProjects.group
                )
            )
            .filter(Project.rr_project_id == rr_project_id)
            .one()
        )

        group: Group = get_or_make_group(
            session,
            project.originating_lab,
            project.originating_address,
        )

        covidhub_users: Iterable[covidtracker.UsersGroups] = covidhub_session.query(
            covidtracker.UsersGroups
        ).filter(
            or_(
                covidtracker.UsersGroups.group_id.in_(
                    covidhub_session.query(covidtracker.Group.id).filter(
                        covidtracker.Group.name.in_(["Admin", "CDPH"])
                    )
                ),
                covidtracker.UsersGroups.group_id.in_(
                    covidhub_session.query(covidtracker.GroupToProjects.group_id)
                    .join(Project)
                    .filter(Project.rr_project_id == rr_project_id)
                ),
            ),
        )

        # create the users!
        for covidhub_user in covidhub_users:
            # try to find the user in the auth0_usermap
            auth0_user = auth0_usermap.get(covidhub_user.user_id, None)
            if auth0_user is None:
                continue

            # try to create this user in the aspen db.
            user = (
                session.query(User).filter(User.email == auth0_user.email).one_or_none()
            )
            if user is None:
                user = User()

            user.name = auth0_user.nickname
            user.email = auth0_user.email
            user.auth0_user_id = auth0_user.auth0_token
            user.group_admin = False
            user.system_admin = covidhub_user.group.name == "Admin"
            user.group = group

        session.commit()
        print(json.dumps({"group_id": group.id}))


def retrieve_auth0_users(config: aspen_config.Config) -> Mapping[str, Auth0Entry]:
    """Retrieves an auth0 token and then retrieve a user list.  Each element of the list
    is a tuple of (name, email, auth0_token)."""
    domain = config.AUTH0_DOMAIN
    client_id = config.AUTH0_MANAGEMENT_CLIENT_ID
    client_secret = config.AUTH0_MANAGEMENT_CLIENT_SECRET

    get_token_response = auth0_authentication.GetToken(domain)
    token = get_token_response.client_credentials(
        client_id, client_secret, "https://{}/api/v2/".format(domain)
    )
    mgmt_api_token = token["access_token"]
    auth0_client = auth0_management.Auth0(domain, mgmt_api_token)

    all_users: MutableMapping[str, Auth0Entry] = dict()
    page = 0
    while True:
        try:
            users_response = auth0_client.users.list(page=page)
            if users_response["length"] == 0:
                # done!
                break

            # concatenate the results to all_users.
            for user in users_response["users"]:
                all_users[user["user_id"]] = Auth0Entry(
                    user["nickname"], user["email"], user["user_id"]
                )
        finally:
            page += 1

    return all_users
