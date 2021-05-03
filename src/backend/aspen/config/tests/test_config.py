import pytest

from aspen.app.aspen_app import AspenApp
from aspen.config import config, testing


def test_subclass_not_flaskproperty():
    """Subclass Config, and fail to annotate a property that is a @flaskproperty."""
    with pytest.raises(Exception):

        class FakeConfig(config.Config, descriptive_name="fake_config"):
            def DEBUG(self) -> bool:
                return True


def test_flaskproperty_from_testconfig(app: AspenApp):
    """Grab the flask properties from TestingConfig, and ensure that we get a reasonable
    list of them."""
    test_config = app.aspen_config
    assert isinstance(test_config, testing.TestingConfig)
    props = test_config.flask_properties()
    assert len(props) == 3
    assert "DEBUG" in props
    assert "SECRET_KEY" in props
    assert "TESTING" in props
