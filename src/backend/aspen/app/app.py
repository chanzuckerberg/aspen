import os
from functools import wraps
from pathlib import Path
from typing import Optional

from authlib.integrations.flask_client import OAuth
from flask import redirect, session
from flask_cors import CORS

from aspen.app.aspen_app import AspenApp
from aspen.config import (
    config,
    DevelopmentConfig,
    LocalConfig,
    ProductionConfig,
    StagingConfig,
)

static_folder = Path(__file__).parent.parent / "static"

# EB looks for an 'application' callable by default.
flask_env = os.environ.get("FLASK_ENV")
aspen_config: Optional[config.Config]
if flask_env == "production":
    aspen_config = ProductionConfig()
elif flask_env == "development":
    aspen_config = DevelopmentConfig()
elif flask_env == "staging":
    aspen_config = StagingConfig()
elif flask_env == "local":
    aspen_config = LocalConfig()
else:
    aspen_config = None

application = AspenApp(
    __name__, static_folder=str(static_folder), aspen_config=aspen_config
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

if flask_env in ("production", "development", "local", "staging"):
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
else:
    auth0 = None


# use this to wrap protected views
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            # Redirect to Login page
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated
