from abc import abstractmethod
from typing import List, Union

import numpy as np
import pandas as pd
from pandas import DataFrame, Series


# Pandas DataFrame/Series extension docs:
# https://pandas.pydata.org/pandas-docs/stable/development/extending.html
class MlSeries(Series):
    @property
    def _constructor(self):
        # return MlSeries
        # For now the same as Pandas Series
        # If custom methods are needed, uncomment first line
        return Series


# Pandas DataFrame/Series extension docs:
# https://pandas.pydata.org/pandas-docs/stable/development/extending.html
class MlDataFrame(DataFrame):
    ###
    # PANDAS METHODS
    ###

    # Properties that should still exist after slicing should be added here
    # _metadata = ['some_property']
    # some_property = 'prop'  # After mutation of this public property, its state is saved and can be used after slicing

    # Abstract method of the Pandas DataFrame class: just calls super class
    @property
    def _constructor_expanddim(self):
        return super()._constructor_expanddim(self)

    # A lot of methods in the DataFrame class return a DataFrame using the _constructor method
    # Every time a new DataFrame is created, we return the inherited DataFrame
    @property
    @abstractmethod
    def _constructor(self):
        return MlDataFrame

    # When slicing methods are called, return custom (inherited) Series object
    @property
    @abstractmethod
    def _constructor_sliced(self):
        return MlSeries

    ###
    # CUSTOM METHODS AND PROPERTIES
    ###

    @property
    def get_df(self):
        return DataFrame(self)

    def downcast(self, signed_cols: bool = None):
        """Automatically check for signed/unsigned columns and downcast.
        However, if a column can be signed while all the data in that column is unsigned, you don't want to downcast to
        an unsigned column. You can explicitly pass these columns.
        """
        print(f'Size before downcasting: {self.memory_usage().sum()} KB')
        for column in self.columns:
            if self[column].dtype in [np.int8, np.int16, np.int32, np.int64]:
                if (self[column] < 0).any() or (signed_cols is not None and self[column].name in signed_cols):
                    print('signed')
                    self[column] = pd.to_numeric(self[column], downcast='signed')
                else:
                    print('unsigned')
                    self[column] = pd.to_numeric(self[column], downcast='unsigned')
            elif self[column].dtype in [np.float16, np.float32, np.float64]:
                self[column] = pd.to_numeric(self[column], downcast='float')
        print(f'Size after downcasting: {self.memory_usage().sum()} KB')

    def reorder_column(self, column: Union[str, List[str]], index: int):
        """Move/reorder a single column or a list of columns to a new index."""
        data_to_be_moved = self[column]
        self.drop(columns=column, inplace=True)
        if isinstance(column, list):
            for i in column:
                self.insert(index, i, data_to_be_moved[i])
                index += 1
        else:
            self.insert(index, column, data_to_be_moved)

    def drop_columns_with_single_values(self, skip_columns: Union[str, List[str]] = None):
        """Drop all columns containing only a single value. This includes all columns that only contain NaN/None.
        """
        columns_to_drop = []
        for column in list(self.columns):
            if skip_columns is not None and column in skip_columns:
                continue
            elif len(self[column].unique()) <= 1:
                columns_to_drop.append(column)
        self.drop(columns=columns_to_drop, inplace=True)

        if not columns_to_drop:
            print('No columns were dropped, could not find a column with only a single value (including NaN/None)')
        else:
            print(f'Columns dropped containing only a single value (including NaN/None): '
                  f'{", ".join(str(column) for column in columns_to_drop)}')
