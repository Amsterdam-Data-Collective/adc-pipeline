from abc import abstractmethod

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
    _metadata = ['some_property']
    some_property = 'prop'  # After mutation of this public property, its state is saved and can be used after slicing

    # Abstract method of the Pandas DataFrame class: just calls super class
    @property
    def _constructor_expanddim(self):
        return super()._constructor_expanddim(self)

    # A lot of methods in the DataFrame class return a DataFrame using the _constructor method
    # Every time a new dataframe is created, we return the inherited dataframe
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

    def return_first_column(self):
        return self.iloc[:, 0]


class TimeDataFrame(MlDataFrame):
    ###
    # PANDAS METHODS
    ###

    # When inheriting, this is the syntax to get properties from both this class and the super class
    _metadata = MlDataFrame._metadata + ['some_other_property']
    some_other_property = 'other_prop'

    # A lot of methods in the DataFrame class return a DataFrame using the _constructor method
    # Every time a new dataframe is created, we return the inherited dataframe
    @property
    def _constructor(self):
        return TimeDataFrame

    # When slicing methods are called, return custom (inherited) Series object
    @property
    def _constructor_sliced(self):
        return super()._constructor_sliced

    ###
    # CUSTOM METHODS AND PROPERTIES
    ###

    def convert_datetime_cols(self, datetime_cols):
        # Convert all date/datetime cols to datetimes
        if not isinstance(datetime_cols, list):
            self[datetime_cols] = pd.to_datetime(self[datetime_cols])
        else:
            for col in datetime_cols:
                if not isinstance(self[col], pd.datetime):
                    self[col] = pd.to_datetime(self[col])


class IssuesWithInitTimeDataFrame(MlDataFrame):
    def __init__(self, datetime_cols, data=None, index=None, columns=None, dtype=None, copy=False):
        super().__init__(data=data, index=index, columns=columns, dtype=dtype, copy=copy)
        self.convert_datetime_cols(datetime_cols=datetime_cols)

    ###
    # PANDAS METHODS
    ###

    # When inheriting, this is the syntax to get properties from both this class and the super class
    _metadata = MlDataFrame._metadata + ['some_other_property']
    some_other_property = 'other_prop'

    # A lot of methods in the DataFrame class return a DataFrame using the _constructor method
    # Every time a new dataframe is created, we return the inherited dataframe
    @property
    def _constructor(self):
        return IssuesWithInitTimeDataFrame

    # When slicing methods are called, return custom (inherited) Series object
    @property
    def _constructor_sliced(self):
        return super()._constructor_sliced

    ###
    # CUSTOM METHODS AND PROPERTIES
    ###

    def convert_datetime_cols(self, datetime_cols):
        # Convert all date/datetime cols to datetimes
        if not isinstance(datetime_cols, list):
            self[datetime_cols] = pd.to_datetime(self[datetime_cols])
        else:
            for col in datetime_cols:
                if not isinstance(self[col], pd.datetime):
                    self[col] = pd.to_datetime(self[col])


class SolvedIssuesWithInitTimeDataFrame(MlDataFrame):
    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False, datetime_cols=None):
        super().__init__(data=data, index=index, columns=columns, dtype=dtype, copy=copy)
        self.datetime_cols = datetime_cols

        if datetime_cols is not None:
            self.convert_datetime_cols()

    ###
    # PANDAS METHODS
    ###

    # When inheriting, this is the syntax to get properties from both this class and the super class
    _metadata = MlDataFrame._metadata + ['some_other_property']
    some_other_property = 'other_prop'

    # A lot of methods in the DataFrame class return a DataFrame using the _constructor method
    # Every time a new dataframe is created, we return the inherited dataframe
    @property
    def _constructor(self):
        return SolvedIssuesWithInitTimeDataFrame

    # When slicing methods are called, return custom (inherited) Series object
    @property
    def _constructor_sliced(self):
        return super()._constructor_sliced

    ###
    # CUSTOM METHODS AND PROPERTIES
    ###

    def convert_datetime_cols(self):
        # Convert all date/datetime cols to datetimes
        if not isinstance(self.datetime_cols, list):
            self[self.datetime_cols] = pd.to_datetime(self[self.datetime_cols])
        else:
            for col in self.datetime_cols:
                if not isinstance(self[col], pd.datetime):
                    self[col] = pd.to_datetime(self[col])


class NiceTimeDataFrame(MlDataFrame):
    def __init__(self, *args, **kwargs):
        self.datetime_cols = kwargs.pop("datetime_cols", None)
        super().__init__(*args, **kwargs)

        if self.datetime_cols is not None:
            self.convert_datetime_cols()

    ###
    # PANDAS METHODS
    ###

    # When inheriting, this is the syntax to get properties from both this class and the super class
    _metadata = MlDataFrame._metadata + ['some_other_property']
    some_other_property = 'other_prop'

    # A lot of methods in the DataFrame class return a DataFrame using the _constructor method
    # Every time a new dataframe is created, we return the inherited dataframe
    @property
    def _constructor(self):
        return NiceTimeDataFrame

    # When slicing methods are called, return custom (inherited) Series object
    @property
    def _constructor_sliced(self):
        return super()._constructor_sliced

    ###
    # CUSTOM METHODS AND PROPERTIES
    ###

    def convert_datetime_cols(self):
        # Convert all date/datetime cols to datetimes
        if not isinstance(self.datetime_cols, list):
            self[self.datetime_cols] = pd.to_datetime(self[self.datetime_cols])
        else:
            for col in self.datetime_cols:
                if not isinstance(self[col], pd.datetime):
                    self[col] = pd.to_datetime(self[col])


@pd.api.extensions.register_dataframe_accessor("mlframe")
class MlDataFrame2:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    # Custom method
    def return_first_column(self):
        return self._obj.iloc[:, 0]
