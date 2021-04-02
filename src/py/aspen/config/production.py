import os
from aspen.config import config


class ProductionConfig(config.RemoteDatabaseConfig, descriptive_name="prod"):
    @config.flaskproperty
    def DEBUG(self) -> bool:
        return False

    @property
    def AUTH0_CALLBACK_URL(self) -> str:
        return f"{os.getenv('API_URL', '')}/callback"
