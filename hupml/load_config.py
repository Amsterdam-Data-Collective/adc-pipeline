import logging.config
from logging import Logger
from typing import Dict

import yaml


class LoadConfig:
    @staticmethod
    def load_yaml_as_dict(path) -> Dict:
        """
        Read yaml file and return settings as a dict.
        Args:
            path: Path to config file.

        Returns:
            Dict with settings.
        """
        with open(file=path, mode='r') as f:
            return yaml.safe_load(f.read())

    @classmethod
    def load_logging_config(cls, path, logger_name=None) -> Logger:
        """
        Load config for logging and return logger with these settings.
        Args:
            path: Path to config file.
            logger_name: Name for the logger to be returned.

        Returns:
            A logger configured as defined in the yaml file.
        """
        config = cls.load_yaml_as_dict(path)
        logging.config.dictConfig(config)
        return logging.getLogger(name=logger_name)
