import logging.config

import yaml


class LoadConfig:
    @staticmethod
    def load_yaml_as_dict(path):
        with open(file=path, mode='r') as f:
            return yaml.safe_load(f.read())

    @classmethod
    def load_logging_config(cls, path, logger_name=None):
        config = cls.load_yaml_as_dict(path)
        logging.config.dictConfig(config)
        return logging.getLogger(name=logger_name)
