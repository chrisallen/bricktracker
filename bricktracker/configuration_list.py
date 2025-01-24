import logging
from typing import Generator

from flask import Flask

from .config import CONFIG
from .configuration import BrickConfiguration
from .exceptions import ConfigurationMissingException

logger = logging.getLogger(__name__)


# Application configuration
class BrickConfigurationList(object):
    app: Flask
    configurations: dict[str, BrickConfiguration]

    # Load configuration
    def __init__(self, app: Flask, /):
        self.app = app

        # Load the configurations only there is none already loaded
        configurations = getattr(self, 'configurations', None)

        if configurations is None:
            logger.info('Loading configuration variables')

            BrickConfigurationList.configurations = {}

            # Process all configuration items
            for config in CONFIG:
                item = BrickConfiguration(**config)

                # Store in the list
                BrickConfigurationList.configurations[item.name] = item

                # Only store the value in the app to avoid breaking any
                # existing variables
                self.app.config[item.name] = item.value

    # Check whether a str configuration is set
    @staticmethod
    def error_unless_is_set(name: str):
        configuration = BrickConfigurationList.configurations[name]

        if configuration.value is None or configuration.value == '':
            raise ConfigurationMissingException(
                '{name} must be defined (using the {environ} environment variable)'.format(  # noqa: E501
                    name=name,
                    environ=configuration.env_name
                ),
            )

    # Get all the configuration items from the app config
    @staticmethod
    def list() -> Generator[BrickConfiguration, None, None]:
        keys = sorted(BrickConfigurationList.configurations.keys())

        for name in keys:
            yield BrickConfigurationList.configurations[name]
