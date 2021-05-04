import os
from urllib.parse import urlencode

from flask import redirect, session

from aspen.app.app import application, auth0


@application.route("/callback")
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get(application.aspen_config.AUTH0_USERINFO_URL)
    userinfo = resp.json()

    # Store the user information in flask session.
    session["jwt_payload"] = userinfo
    session["profile"] = {
        "user_id": userinfo["sub"],
        "name": userinfo["name"],
    }
    return redirect(os.getenv("FRONTEND_URL") + "/data/samples")


@application.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=application.aspen_config.AUTH0_CALLBACK_URL
    )


@application.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {
        "returnTo": os.getenv("FRONTEND_URL"),
        "client_id": application.aspen_config.AUTH0_CLIENT_ID,
    }
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))
