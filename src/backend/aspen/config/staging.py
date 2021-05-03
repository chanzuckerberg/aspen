import logging

from aspen import aws
from aspen.config import config

logger = logging.getLogger(__name__)


class StagingConfig(config.RemoteDatabaseConfig, descriptive_name="staging"):
    @config.flaskproperty
    def DEBUG(self) -> bool:
        return True

    @property
    def AUTH0_CALLBACK_URL(self) -> str:
        eb_env_name = aws.elasticbeanstalk.get_environment_suffix()
        logger.info(f"DETECTED EB_ENV as {eb_env_name}")
        return (
            f"http://aspen-{eb_env_name}.{aws.region()}.elasticbeanstalk.com/callback"
        )
