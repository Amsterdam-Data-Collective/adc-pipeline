import logging
from abc import abstractmethod
from typing import List, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MlSeries(pd.Series):
    """
    This class is an extension of the Pandas DataFrame class, to provide extra functionality. In order to let this class
    work correctly, there are a few Pandas methods and properties that need to be implemented as specified by the docs.
    These methods are highlighted with comments.

    Docs: https://pandas.pydata.org/pandas-docs/stable/development/extending.html
    """

    ###
    # PANDAS METHODS
    ###

    @property
    def _constructor(self):
        """
        A lot of methods in the DataFrame class return a Series using the _constructor method.
        Every time a new Series is created, we return our Series instead of a Pandas Series.
        """
        ###
        # NOTE:
        # For now the same as Pandas Series
        # If custom methods are needed, uncomment the following line:
        # return MlSeries
        ###
        return pd.Series

    ###
    # CUSTOM METHODS AND PROPERTIES
    ###

    # PLACEHOLDER: Nothing is added for series yet, add functionality here and delete this comment.


class MlDataFrame(pd.DataFrame):
    """
    This class is an extension of the Pandas DataFrame class, to provide extra functionality. In order to let this class
    work correctly, there are a few Pandas methods and properties that need to be implemented as specified by the docs.
    These methods are highlighted with comments.

    Docs: https://pandas.pydata.org/pandas-docs/stable/development/extending.html
    """
    ###
    # PANDAS METHODS
    ###

    """Properties that should be persistent (still exist after slicing) should be added here"""
    _metadata = ['pandas_df', 'memory_size']

    @property
    def _constructor_expanddim(self):
        """Abstract method of the Pandas DataFrame class: just calls super class."""
        return super()._constructor_expanddim(self)

    @property
    @abstractmethod
    def _constructor(self):
        """
        A lot of methods in the DataFrame class return a DataFrame using the _constructor method.
        Every time a new DataFrame is created, we return the our DataFrame instead of a Pandas DataFrame.
        """
        return MlDataFrame

    @property
    @abstractmethod
    def _constructor_sliced(self):
        """When slicing methods are called, return custom (inherited) Series object"""
        return MlSeries

    ###
    # CUSTOM METHODS AND PROPERTIES
    ###

    @property
    def pandas_df(self) -> pd.DataFrame:
        """
        Returns:
            Casted Pandas Dataframe from MlDataFrame
        """
        return pd.DataFrame(self)

    @property
    def memory_size(self) -> float:
        """
        Returns:
            Memory size of the full DataFrame in KB
        """
        return self.memory_usage().sum()

    def downcast(self, signed_cols: bool = None) -> None:
        """
        Automatically check for signed/unsigned columns and downcast.
        However, if a column can be signed while all the data in that column is unsigned, you don't want to downcast to
        an unsigned column. You can explicitly pass these columns.
        Args:
            signed_cols: Columns that can be signed (= positive and negative values, unsigned = only positive values).
        """
        logger.info(f'Size before downcasting: {self.memory_size} KB')
        for column in self.columns:
            if self[column].dtype in [np.int8, np.int16, np.int32, np.int64]:
                if (self[column] < 0).any() or (signed_cols is not None and self[column].name in signed_cols):
                    self[column] = pd.to_numeric(self[column], downcast='signed')
                else:
                    self[column] = pd.to_numeric(self[column], downcast='unsigned')
            elif self[column].dtype in [np.float16, np.float32, np.float64]:
                self[column] = pd.to_numeric(self[column], downcast='float')
        logger.info(f'Size after downcasting: {self.memory_size} KB')

    def reorder_columns(self, columns: Union[str, List[str]], index: int) -> None:
        """
        Move/reorder a single column or a list of columns to a new index.
        Args:
            columns: Columns to move to a new index.
            index: Index where the column(s) will be moved to.
        """
        data_to_be_moved = self[columns]
        self.drop(columns=columns, inplace=True)
        if isinstance(columns, list):
            for column in columns:
                self.insert(index, column, data_to_be_moved[column])
                index += 1
        else:
            self.insert(index, columns, data_to_be_moved)

    def drop_columns_with_single_values(self, skip_columns: Union[str, List[str]] = None) -> None:
        """
        Drop all columns containing only a single value. This includes all columns that only contain NaN/None.
        Args:
            skip_columns: Columns to skip
        """
        columns_to_drop = []
        for column in list(self.columns):
            if skip_columns is not None and column in skip_columns:
                continue
            elif len(self[column].unique()) <= 1:
                columns_to_drop.append(column)
        self.drop(columns=columns_to_drop, inplace=True)

        if not columns_to_drop:
            logger.info('No columns were dropped, could not find a column with only a single value (incl. NaN/None)')
        else:
            logger.info(f'Columns dropped containing only a single value (incl. NaN/None): '
                        f'{", ".join(str(column) for column in columns_to_drop)}')

    def factorize_columns(self, columns: Union[str, List[str]]) -> None:
        """
        Convert columns to a list of unique integers per category
        Args:
            columns: Columns to convert to a list of unique integers per category
        """
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            self[column], _ = pd.factorize(self[column])

    def keep_top_items_in_columns(self, columns: Union[str, List[str]], number_of_items: int) -> None:
        """
        For all the columns passed in the arguments, keep the N-top frequent items. The rest will be set to 'other'.
        Args:
            columns: Columns to only keep N-top frequent items.
            number_of_items: The top number of items to keep (= N).
        """
        if not isinstance(columns, List):
            columns = [columns]

        for column in columns:
            counter_list = self[column].value_counts()
            top_items_list = counter_list[:number_of_items].index.tolist()
            self[column].loc[~np.array(self[column].isin(top_items_list))] = 'other'
