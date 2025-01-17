from typing import Generator

from flask import current_app, Flask

from .config import CONFIG
from .configuration import BrickConfiguration
from .exceptions import ConfigurationMissingException


# Application configuration
class BrickConfigurationList(object):
    app: Flask

    # Load configuration
    def __init__(self, app: Flask, /):
        self.app = app

        # Process all configuration items
        for config in CONFIG:
            item = BrickConfiguration(**config)
            self.app.config[item.name] = item

    # Check whether a str configuration is set
    @staticmethod
    def error_unless_is_set(name: str):
        value = current_app.config[name].value

        if value is None or value == '':
            raise ConfigurationMissingException(
                '{name} must be defined'.format(name=name),
            )

    # Get all the configuration items from the app config
    @staticmethod
    def list() -> Generator[BrickConfiguration, None, None]:
        keys = list(current_app.config.keys())
        keys.sort()

        for name in keys:
            config = current_app.config[name]

            if isinstance(config, BrickConfiguration):
                yield config
