import os
import shutil

import pandas as pd

from adcpipeline import PipelineBase

data = pd.DataFrame(data=[[1, 2, 3], [4, 5, 6]])


class Pipeline(PipelineBase):
    def print_text_from_argument(self, text='asfd'):
        print(text)

    def print_predefined_text(self):
        print('Predefined text')

    def n_times_squared(self, value: int, n: int):
        result = value
        for i in range(0, n):
            result = result ** 2
        print(f'Squaring the number {value} for {n} times in a row gives = {result}')

    def square_df(self):
        print('Square elements in dataframe')
        self.df = self.df ** 2


class TestPipeline:
    def test_with_settings_from_code(self):
        method_settings = [
            {'print_text_from_argument': {'text': 'This is the text passed to the method'}},
            {'print_text_from_argument': {'text': 1}},
            {'print_predefined_text': None},
            {'n_times_squared': {'value': 2, 'n': 2}},
            {'print_text_from_argument': {'text': 'Same method is called again, but later in the pipeline'}},
            {'square_df': None}
        ]
        p = Pipeline(df=data, method_settings=method_settings)
        p.run()
        assert p.df.equals(pd.DataFrame(data=[[1, 4, 9], [16, 25, 36]])) is True

    def test_with_settings_from_yaml(self):
        p = Pipeline.from_yaml_file(df=data, path='tests/configs/pipeline_settings1.yaml')
        p.run()
        assert p.df.equals(pd.DataFrame(data=[[1, 4, 9], [16, 25, 36]])) is True

    def test_caching(self):
        method_settings = [
            {'square_df': None},
            {'print_predefined_text': None},
            {'square_df': None},
            {'print_predefined_text': None},
        ]
        p = Pipeline(df=data, method_settings=method_settings, filename='test_cache')
        p.run_or_load()
        p.run_or_load()
        assert os.path.isfile('./cache/test_cache.pkl')
        assert p.df.equals(pd.DataFrame(data=[[1, 16, 81], [256, 625, 1296]])) is True
        shutil.rmtree('./cache')

    def test_caching_with_steps(self):
        method_settings = [
            {'square_df': None},
            {'print_predefined_text': None},
            {'square_df': None},
            {'print_predefined_text': None},
        ]
        p = Pipeline(df=data, method_settings=method_settings, filename='test_cache')
        p.run_or_load(load_cache_from_step=1)
        p.run_or_load(load_cache_from_step=1)
        assert os.path.isfile('./cache/test_cache_step1.pkl')
        assert p.df.equals(pd.DataFrame(data=[[1, 16, 81], [256, 625, 1296]])) is True
        shutil.rmtree('./cache')
