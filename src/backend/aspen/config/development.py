from aspen.config import config


class DevelopmentConfig(config.Config, descriptive_name="dev"):
    @config.flaskproperty
    def DEBUG(self) -> bool:
        return True

    @property
    def AUTH0_CALLBACK_URL(self) -> str:
        return "http://localhost:3000/callback"

    @property
    def DATABASE_URI(self) -> str:
        return "postgresql://user_rw:password_rw@localhost:5432/aspen_db"
