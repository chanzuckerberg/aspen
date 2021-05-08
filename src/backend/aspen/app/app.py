from functools import wraps
from pathlib import Path

from authlib.integrations.flask_client import OAuth
from flask import redirect, session
from flask_cors import CORS

from aspen.app.aspen_app import AspenApp
from aspen.config.docker_compose import DockerComposeConfig

static_folder = Path(__file__).parent.parent / "static"

application = AspenApp(
    __name__, static_folder=str(static_folder), aspen_config=DockerComposeConfig()
)
# FIXME(mbarrien): Make this more restrictive
allowed_origin = ["*"]
CORS(
    application,
    max_age=600,
    supports_credentials=True,
    origins=allowed_origin,
    allow_headers=["Content-Type"],
)

oauth = OAuth(application)
auth0 = oauth.register(
    "auth0",
    client_id=application.aspen_config.AUTH0_CLIENT_ID,
    client_secret=application.aspen_config.AUTH0_CLIENT_SECRET,
    api_base_url=application.aspen_config.AUTH0_BASE_URL,
    access_token_url=application.aspen_config.AUTH0_ACCESS_TOKEN_URL,
    authorize_url=application.aspen_config.AUTH0_AUTHORIZE_URL,
    client_kwargs=application.aspen_config.AUTH0_CLIENT_KWARGS,
)


# use this to wrap protected views
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            # Redirect to Login page
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated
