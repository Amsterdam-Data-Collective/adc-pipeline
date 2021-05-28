import logging
import os
import re
from abc import ABC
from typing import Callable, Dict, List, Iterator, Optional

import pandas as pd
import yaml
from pandas import DataFrame

logger = logging.getLogger(__name__)


class PipelineBase(ABC):
    _methods_settings: List[Dict] = []
    _method_list: List[Callable] = []

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

    def __init__(self, df: Optional[DataFrame], method_settings: List, filename: str = None) -> None:
        self.df = df
        self.method_settings = method_settings
        self.step = 0
        self.path = None
        if filename is None:
            return
        if len(re.split(r'/\\', filename)) == 1:  # Filename is a path with directory
            if filename is not None and not os.path.exists('cache'):
                os.makedirs('cache')
            self.path = os.path.join('cache/', f"{filename}")
        self.path = os.path.join(f"{self.path}.pkl")

    @classmethod
    def from_yaml_file(cls, df: DataFrame, path: str, filename: str = None):
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
            filename: Path/filename for caching

        Returns:
            Instance of this class.
        """
        with open(file=path, mode='r') as f:
            settings = yaml.safe_load(f.read())['pipeline']
        return cls(df=df, method_settings=settings, filename=filename)

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

    def run(self) -> None:
        """
        This will call all the lambdas (in order) saved in the 'method_list'. These methods can be set with the
        property 'method_settings'.
        """
        logger.info(f'Running pipeline using the following settings: {self.method_settings}')
        for method in self.method_list:
            method()
        if self.path is not None and self.df is not None:
            self.df.to_pickle(self.path)

    def run_or_load(self, load_cache_from_step: int = None) -> None:
        """
        Instead of running the pipeline, load the result from the pipeline from a cache file. Useful functionality
        if you have not modified the pipeline, but want to use the output. Beware that if you change the pipeline, you
        should re-run the pipeline first or remove the cache. Otherwise this method will load incorrect results.
        Alternatively you can provide the from_step parameter to load the first N steps from cache and only execute
        the steps afterwards
        Args:
            load_cache_from_step (Optional): Determine from which step onwards you want to load the cache and continue with
                executing the pipeline. Each method is accounted as a single step

        """
        if self.path is None:
            raise ValueError("Mode not possible without a valid filename attribute in class initiation")
        if load_cache_from_step is not None:
            assert isinstance(load_cache_from_step, int), "Please provide an int as from_step parameter"
            step_path = f"{self.path.rstrip('.pkl')}_step{load_cache_from_step}.pkl"
            if os.path.isfile(step_path):
                self.df = pd.read_pickle(step_path)
                for method in self.method_list[load_cache_from_step:]:
                    method()
            else:
                for idx, method in enumerate(self.method_list):
                    if idx == load_cache_from_step and self.df is not None:
                        self.df.to_pickle(step_path)
                    method()
        else:
            if os.path.isfile(self.path):
                self.df = pd.read_pickle(self.path)
            else:
                self.run()
