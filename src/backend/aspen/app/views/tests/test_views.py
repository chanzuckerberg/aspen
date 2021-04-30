import json

from aspen.database.models.usergroup import User
from aspen.test_infra.models.usergroup import group_factory, user_factory


def test_usergroup_view_get(session, app, client):
    group = group_factory()
    user = user_factory(group)
    session.add(group)
    session.commit()
    with client.session_transaction() as sess:
        sess["profile"] = {"name": user.name, "user_id": user.auth0_user_id}
    res = client.get("/api/usergroup")
    expected = {"user": user.to_dict(), "group": group.to_dict()}
    assert expected == json.loads(res.get_data(as_text=True))


def test_usergroup_view_put_pass(session, app, client):
    group = group_factory()
    user = user_factory(group, agreed_to_tos=False)
    session.add(group)
    session.commit()
    with client.session_transaction() as sess:
        sess["profile"] = {"name": user.name, "user_id": user.auth0_user_id}

    data = {"agreed_to_tos": True}
    res = client.put("/api/usergroup", json=data, content_type="application/json")

    # start a new transaction
    session.close()
    session.begin()
    updated_user = (
        session.query(User).filter(User.auth0_user_id == user.auth0_user_id).one()
    )
    assert updated_user.agreed_to_tos
    assert res.status == "200 OK"


def test_usergroup_view_put_fail(session, app, client):
    group = group_factory()
    user = user_factory(group, agreed_to_tos=False)
    session.add(group)
    session.commit()
    with client.session_transaction() as sess:
        sess["profile"] = {"name": user.name, "user_id": user.auth0_user_id}

    data = {"fake_field": "even faker"}
    res = client.put("/api/usergroup", json=data, content_type="application/json")

    assert res.status == "400 BAD REQUEST"


def test_redirect(app, client):
    res = client.get("api/usergroup")
    assert res.status == "302 FOUND"
    redirect_text = b'You should be redirected automatically to target URL: <a href="/login">/login</a>'
    assert redirect_text in res.data
