from functools import lru_cache
from typing import Optional

from flask import Flask

from aspen.config.config import Config
from aspen.database import connection as aspen_database


class AspenApp(Flask):
    def __init__(self, *args, aspen_config: Optional[Config], **kwargs):
        super().__init__(*args, **kwargs)
        self._aspen_config = aspen_config
        if self._aspen_config is not None:
            self.config.from_mapping(**self._aspen_config.flask_properties())

    def _inject_config(self, aspen_config: Config):
        self._aspen_config = aspen_config
        self.config.from_mapping(**self._aspen_config.flask_properties())

    @property
    def aspen_config(self) -> Config:
        if self._aspen_config is None:
            raise ValueError("aspen config not set")
        return self._aspen_config

    @lru_cache()
    def _DATABASE_INTERFACE(self, uri: str) -> aspen_database.SqlAlchemyInterface:
        return aspen_database.init_db(uri)

    @property
    def DATABASE_INTERFACE(self) -> aspen_database.SqlAlchemyInterface:
        return self._DATABASE_INTERFACE(self.aspen_config.DATABASE_URI)
