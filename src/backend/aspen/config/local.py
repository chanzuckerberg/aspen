import os
import uuid

from aspen.config import config


# Docker-compose environment config
class LocalConfig(config.Config, descriptive_name="local"):
    @config.flaskproperty
    def DEBUG(self) -> bool:
        return True

    @config.flaskproperty
    def SECRET_KEY(self) -> str:
        if os.getenv("FLASK_SECRET_KEY"):
            return os.getenv("FLASK_SECRET_KEY", "")
        return uuid.uuid4().hex

    @config.flaskproperty
    def SESSION_COOKIE_SECURE(self) -> bool:
        return True

    @config.flaskproperty
    def SESSION_COOKIE_HTTPONLY(self) -> bool:
        return True

    @config.flaskproperty
    def SESSION_COOKIE_SAMESITE(self) -> str:
        return "Lax"

    @property
    def DATABASE_URI(self) -> str:
        return "postgresql://user_rw:password_rw@database:5432/aspen_db"

    @property
    def AUTH0_CALLBACK_URL(self) -> str:
        return "http://localhost:3000/callback"
