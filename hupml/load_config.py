import logging.config
from logging import Logger
from typing import Dict

import yaml


class LoadConfig:
    @staticmethod
    def load_yaml_as_dict(path: str) -> Dict:
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
    def load_logger_from_config(cls, path: str, logger_name: str = None,
                                overwrite_file_name_path: str = None) -> Logger:
        """
        Load config for logging and return logger with these settings.
        Args:
            path: Path to config file.
            logger_name: Name for the logger to be returned.
            overwrite_file_name_path: Overwrites the path to the logging file as configured in the .yaml file.

        Returns:
            A logger configured as defined in the yaml file.
        """
        config = cls.load_yaml_as_dict(path)
        if overwrite_file_name_path:
            config["handlers"]['file_handler']['filename'] = overwrite_file_name_path
        logging.config.dictConfig(config)
        return logging.getLogger(name=logger_name)
