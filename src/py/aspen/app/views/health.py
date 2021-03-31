from flask import Response

from aspen.app.app import application


@application.route("/health", methods=["GET"])
def health():
    health_check = Response(response="healthy", status=200)
    print(health_check)
    return health_check
