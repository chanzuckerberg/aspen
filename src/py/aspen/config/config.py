from __future__ import annotations

import json
import os
import platform
from collections import MutableMapping
from functools import lru_cache
from typing import Any, Callable, Mapping, Optional, Set, Type, TypeVar, Union

import boto3
from botocore.exceptions import ClientError

from aspen import aws

ConfigLike = TypeVar("ConfigLike", bound="Config")


def flaskproperty(
    original_method: Callable[[ConfigLike], Any]
) -> Callable[[ConfigLike], Any]:
    """Annotation to apply to a method to indicate that it is a property to be passed
    to flask's config.

    It should be applied to a method in a Config object, and it has to be co-equal in
    rank to @abc.abstractmethod.  No annotation other than @abc.abstractmethod should
    follow this one.

    For example, both are acceptable:
        @flaskproperty
        @abc.abstractmethod
        def DEBUG(self):
            ...

        @abc.abstractmethod
        @flaskproperty
        def DEBUG(self):
            ...
    """
    original_method.__is_flaskproperty__ = True  # type: ignore
    return original_method


def _get_flaskproperty_names(obj: Union[Type[Config], Config]) -> Set[str]:
    """Given a Config object or a Config class, return a collection of method names that
    have the @flaskproperty annotation."""
    result: Set[str] = set()
    for attrib_name in dir(obj):
        try:
            attrib_value = getattr(obj, attrib_name)
            if callable(attrib_value) and getattr(attrib_value, "__is_flaskproperty__"):
                result.add(attrib_name)
        except Exception:
            continue

    return result


class Config(object):
    _config_flask_properties: Optional[Set[str]] = None
    _subclasses: MutableMapping[str, Type[Config]] = dict()

    def __init_subclass__(
        cls: Type[Config], descriptive_name: Optional[str] = None, *args, **kwargs
    ):
        # the type: ignore on the next line is due to
        # https://github.com/python/mypy/issues/4660
        super().__init_subclass__(*args, **kwargs)  # type: ignore
        if descriptive_name is not None:
            Config._subclasses[descriptive_name] = cls

            # get a list of @flaskproperties for Config and the subclass of Config, and
            # compare to see if there are any attributes that were marked as
            # @flaskproperty in Config but not in the subclass.
            if Config._config_flask_properties is None:
                Config._config_flask_properties = _get_flaskproperty_names(Config)
            flask_properties = _get_flaskproperty_names(cls)

            if not Config._config_flask_properties.issubset(flask_properties):
                missing_properties = Config._config_flask_properties - flask_properties
                missing_properties_string = ", ".join(missing_properties)
                raise Exception(
                    f"Attributes ({missing_properties_string}) defined as flask properties"
                    f" in Config but not in {cls.__name__}"
                )

    @classmethod
    def by_descriptive_name(cls, descriptive_name: str) -> Config:
        return Config._subclasses[descriptive_name]()

    ####################################################################################
    # AWS secrets
    @lru_cache()
    def _AWS_SECRET(self) -> Mapping[str, Any]:
        # this extra level of indirection
        # (Auth0Config.AWS_SECRET -> Auth0Config._AWS_SECRET()) is because of
        # https://github.com/python/mypy/issues/1362
        session = aws.session()

        secret_name = os.environ.get("AUTH0_CONFIG_SECRET_NAME", "aspen-config")
        client = session.client(
            service_name="secretsmanager", endpoint_url=os.getenv("BOTO_ENDPOINT_URL")
        )

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise e
        else:
            secret = get_secret_value_response["SecretString"]
            return json.loads(secret)

    @property
    def AWS_SECRET(self) -> Mapping[str, Any]:
        return self._AWS_SECRET()

    ####################################################################################
    # flask properties
    def flask_properties(self) -> Mapping[str, Any]:
        """Get a mapping from method name to the value from calling the method, for all
        the methods that are annotated as @flaskproperty."""
        result: MutableMapping[str, Any] = dict()
        for attrib_name in dir(self):
            try:
                attrib_value = getattr(self, attrib_name)
                if not (
                    callable(attrib_value)
                    and getattr(attrib_value, "__is_flaskproperty__")
                ):
                    continue
            except Exception:
                continue
            else:
                result[attrib_name] = attrib_value()

        return result

    @flaskproperty
    def DEBUG(self) -> bool:
        return False

    @flaskproperty
    def SECRET_KEY(self) -> str:
        return platform.node()

    @flaskproperty
    def TESTING(self) -> bool:
        return False

    ####################################################################################
    # auth0 properties
    @property
    def AUTH0_CLIENT_ID(self) -> str:
        return self.AWS_SECRET["AUTH0_CLIENT_ID"]

    @property
    def AUTH0_CALLBACK_URL(self) -> str:
        raise NotImplementedError()

    @property
    def AUTH0_CLIENT_SECRET(self) -> str:
        return self.AWS_SECRET["AUTH0_CLIENT_SECRET"]

    @property
    def AUTH0_MANAGEMENT_CLIENT_ID(self) -> str:
        return self.AWS_SECRET["AUTH0_MANAGEMENT_CLIENT_ID"]

    @property
    def AUTH0_MANAGEMENT_CLIENT_SECRET(self) -> str:
        return self.AWS_SECRET["AUTH0_MANAGEMENT_CLIENT_SECRET"]

    @property
    def AUTH0_DOMAIN(self) -> str:
        return self.AWS_SECRET["AUTH0_DOMAIN"]

    @property
    def AUTH0_BASE_URL(self) -> str:
        try:
            return self.AWS_SECRET["AUTH0_BASE_URL"]
        except KeyError:
            return f"https://{self.AUTH0_DOMAIN}"

    @property
    def AUTH0_ACCESS_TOKEN_URL(self) -> str:
        try:
            return self.AWS_SECRET["AUTH0_ACCESS_TOKEN_URL"]
        except KeyError:
            return f"{self.AUTH0_BASE_URL}/oauth/token"

    @property
    def AUTH0_AUTHORIZE_URL(self) -> str:
        try:
            return self.AWS_SECRET["AUTH0_AUTHORIZE_URL"]
        except KeyError:
            return f"{self.AUTH0_BASE_URL}/authorize"

    @property
    def AUTH0_CLIENT_KWARGS(self) -> Mapping[str, Any]:
        try:
            return self.AWS_SECRET["AUTH0_CLIENT_KWARGS"]
        except KeyError:
            return {
                "scope": "openid profile email",
            }

    @property
    def AUTH0_USERINFO_URL(self) -> str:
        try:
            return self.AWS_SECRET["AUTH0_USERINFO_URL"]
        except KeyError:
            return "userinfo"

    ####################################################################################
    # database properties
    @property
    # TODO: This should be an abstract method as well.
    def DATABASE_URI(self) -> str:
        raise NotImplementedError()

    @property
    def DATABASE_READONLY_URI(self) -> str:
        raise NotImplementedError()


class RemoteDatabaseConfig(Config):
    """Configuration for running with a remote database."""

    @flaskproperty
    def SECRET_KEY(self) -> str:
        return self.AWS_SECRET["FLASK_SECRET"]

    @property
    def DATABASE_URI(self) -> str:
        username = self.AWS_SECRET["DB"]["rw_username"]
        password = self.AWS_SECRET["DB"]["rw_password"]

        instance_address = None
        try:
            instance_address = self.AWS_SECRET["DB"]["address"]
        except KeyError:
            rds = boto3.client("rds")
            response = rds.describe_db_instances(DBInstanceIdentifier="aspen-db")
            instance_info = response["DBInstances"][0]
            instance_address = instance_info["Endpoint"]["Address"]
        instance_port = instance_info["Endpoint"]["Port"]
        db_name = os.getenv("RDEV_PREFIX", 'aspen_db')
        return f"postgresql://{username}:{password}@{instance_address}:{instance_port}/{db_name}"
