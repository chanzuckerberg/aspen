from pathlib import Path

from flask import send_from_directory

from aspen.app.app import application, requires_auth


# Catch all routes. If path is a file, send the file;
# else send index.html. Allows reloading React app from any route.
@application.route("/", defaults={"path": ""})
@application.route("/<path:path>")
@requires_auth
def serve(path):
    if path != "" and Path(application.static_folder + "/" + path).exists():
        return send_from_directory(application.static_folder, path)
    else:
        return send_from_directory(application.static_folder, "index.html")
