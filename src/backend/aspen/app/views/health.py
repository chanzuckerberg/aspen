from flask import Response

from aspen.app.app import application


@application.route("/health", methods=["GET"])
def health():
    """
    Provide an endpoint that AWS Load Balancers can use to determine
    whether this service is healthy.
    """
    health_check = Response(response="healthy", status=200)
    return health_check
