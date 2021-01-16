import os
from pathlib import Path

from covidr.config import DevelopmentConfig
from flask import Flask, send_from_directory

static_folder = Path("static")

# EB looks for an 'application' callable by default.
application = Flask(__name__, static_folder=str(static_folder))


if os.environ.get("FLASK_ENV") == "development":
    application.config.from_object(DevelopmentConfig())


# Catch all routes. If path is a file, send the file;
# else send index.html. Allows reloading React app from any route.
@application.route("/", defaults={"path": ""})
@application.route("/<path:path>")
def serve(path):
    if path != "" and Path(application.static_folder + "/" + path).exists():
        return send_from_directory(application.static_folder, path)
    else:
        return send_from_directory(application.static_folder, "index.html")