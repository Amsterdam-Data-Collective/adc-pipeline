import os
import logging
import pandas as pd
from abc import ABC
from typing import Callable, Dict, List, Iterator

from pandas import DataFrame

from hupml.load_config import LoadConfig

logger = logging.getLogger(__name__)


class PipelineBase(ABC):
    _methods_settings: List[Dict] = []
    _method_list: List[Callable] = []

    def __init__(self, df: DataFrame, method_settings: List, filename: str = None, data_folder: str = 'data/') -> None:
        self._step = 0
        self.path = os.path.join(data_folder, filename) if filename is not None else None
        self.df = df
        self.method_settings = method_settings

    def __get_lambda_method(self, setting: Dict) -> Callable:
        """
        Args:
            setting: The key is the name of the method, the value is a dict containing the argument names and
            corresponding values.
        Returns:
            A lambda containing a method with method parameters to be called when the lambda is called.
        """
        method_name, method_params = list(setting.items())[0]

        # Consistency checks
        if len(setting.items()) > 1:
            raise ValueError('There should be only one dict available for setting')
        if not isinstance(method_name, str):
            raise TypeError('The method name should be a string')
        if method_params is not None:
            for key in method_params.keys():
                if not isinstance(key, str):
                    raise TypeError('Argument names for methods should be strings')

        # Get lambda
        method = getattr(self, method_name)
        if method_params is None:
            return lambda: method()
        else:
            return lambda: method(**method_params)

    @property
    def method_settings(self) -> List[Dict]:
        """
        Returns:
            A list of dicts containing the methods and corresponding arguments that will be called (in order) when
            the pipeline is run. Format: [{<method_name>: {<argument_name>: <argument_value>}}, ...]
        """
        return self._methods_settings

    @method_settings.setter
    def method_settings(self, methods_settings: List[Dict]) -> None:
        """
        This method saves the list of dicts as property and converts all methods and corresponding arguments to callable
        lambdas. These lambdas are saved in the property 'method_list'.
        Args:
            methods_settings: A list of dicts containing the methods and corresponding arguments that will be called
            (in order) when the pipeline is run. Format: [{<method_name>: {<argument_name>: <argument_value>}}, ...]
        """
        self._methods_settings = methods_settings
        self._method_list = []
        for setting in methods_settings:
            self._method_list.append(self.__get_lambda_method(setting))

    @property
    def method_list(self) -> List[Callable]:
        """
        Returns:
            A list of callable lambdas, as defined by the property 'method_settings'. These are called in order by the
            when the pipeline is run.
        """
        return self._method_list

    @classmethod
    def from_yaml_file(cls, df: DataFrame, path: str):
        """
        This is a factory method to instantiate this class by loading the settings from a yaml file.
        Format of yaml file should be:
        pipeline:
          - <method_name>: {<argument_name>: <argument_value>}
          - <method_name>: {<argument_name>: <argument_value>}
          - ...
        Args:
            df: This is your data in a DataFrame format.
            path: Path to yaml file.

        Returns:
            Instance of this class.
        """
        settings = LoadConfig.load_yaml_as_dict(path)['pipeline']
        return cls(df=df, method_settings=settings)

    def __call__(self) -> None:
        self.run()

    def __repr__(self) -> str:
        return str(self.method_settings)

    def __getitem__(self, i: int) -> Dict:
        return self.method_settings[i]

    def __setitem__(self, i: int, setting: Dict) -> None:
        self.method_settings[i] = setting
        self._method_list[i] = self.__get_lambda_method(setting)

    def __delitem__(self, i: int) -> None:
        del self.method_settings[i]
        del self.method_list[i]

    def __len__(self) -> int:
        return len(self.method_settings)

    def __iter__(self) -> Iterator[Dict]:
        return iter(self.method_settings)

    def __reversed__(self) -> List[Dict]:
        return list(reversed(self.method_settings))

    def insert(self, index: int, setting: Dict) -> None:
        self.method_settings.insert(index, setting)
        self.method_list.insert(index, self.__get_lambda_method(setting))

    def reset(self) -> None:
        """
        Reset the current step of the pipeline to 0
        """
        self._step = 0

    def run(self, steps: int = None) -> None:
        """
        This will call all the lambdas (in order) saved in the 'method_list'. These methods can be set with the
        property 'method_settings'.
        Args:
            steps: instead of running all methods in the method list, run an N amount of methods.
        """
        if steps is None:
            steps = len(self.method_list)
        if self._step >= len(self.method_list):
            logger.info("Pipeline already ran all methods, run pipeline.reset() before running again")
            return
        till_step = min(self._step + steps, len(self.method_settings))
        current_methods = self.method_settings[self._step: till_step]
        logger.info(f'Running pipeline using the following settings: {current_methods}')
        for method in self.method_list[self._step: till_step]:
            logger.info(f"Executing method {method}")
            method()
        self._step += steps
        if self.path is not None:
            self.df.to_pickle(self.path)

    def run_or_load(self) -> None:
        """
        If filename is defined in the constructor of the class a cache is made with the results of the pipeline.
        Use this method to load the cache if available or run the pipeline if not.
        """
        if self.path is None:
            raise ValueError("Mode not possible without a valid filename")
        if os.path.isfile(self.path):
            self.df = pd.read_pickle(self.path)
        else:
            self.run()
