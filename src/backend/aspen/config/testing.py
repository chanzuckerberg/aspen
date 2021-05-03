import uuid

from aspen.config import config


class TestingConfig(config.Config, descriptive_name="test"):
    def __init__(self, db_uri):
        self.db_uri = db_uri

    @config.flaskproperty
    def TESTING(self):
        return True

    @config.flaskproperty
    def SECRET_KEY(self):
        return uuid.uuid4().hex

    @property
    def AUTH0_CALLBACK_URL(self):
        return None

    @property
    def DATABASE_URI(self):
        return self.db_uri
