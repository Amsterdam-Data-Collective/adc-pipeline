import logging
import os
from typing import List

import pandas as pd
from sqlalchemy import create_engine

from hupml.load_config import LoadConfig

logger = logging.getLogger(__name__)


class DbConnection:
    def __init__(self, sql_config_path: str, use_cache: bool = False, cache_directory_path: str = None) -> None:
        """
        For more info on connection strings: https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls.
        General format is dialect+driver://username:password@host:port/database.
        Args:
            sql_config_path: Path to database configuration settings (.yaml file).
            use_cache: Uses cache if True. If no cache is available, a new one is made.
            cache_directory_path: The path to the directory to find/save all the cache files.
        """
        conn_settings = LoadConfig.load_yaml_as_dict(sql_config_path)['connection_settings']
        conn_str = f"{conn_settings['dialect']}+{conn_settings['driver']}:" \
                   f"//{conn_settings['user']}:{conn_settings['passwd']}" \
                   f"@{conn_settings['host']}/{conn_settings['database']}"
        self.database_name = conn_settings['database']
        self.engine = create_engine(conn_str)
        self.use_cache = use_cache
        if use_cache and cache_directory_path is None:
            raise ValueError("The argument 'cache_path' cannot be None if 'use_cache' is True.")
        self.cache_directory_path = cache_directory_path

    def df_from_query(self, query: str, parse_dates: List[str] = None) -> pd.DataFrame:
        """
        Executes a query and loads the results into a Pandas DataFrame.
        Args:
            query: Sql query to execute.
            parse_dates: List of column names to parse as dates.

        Returns:
            A Pandas DataFrame with the results of the query.
        """
        logger.info(f"Executing query in the '{self.database_name}' database...")
        return pd.read_sql_query(sql=query, con=self.engine, parse_dates=parse_dates)

    def df_from_sql_file(self, sql_file_path: str, parse_dates: List[str] = None) -> pd.DataFrame:
        """
        Executes a (single) query from a file and loads the results into a Pandas DataFrame.
        Args:
            sql_file_path: Path to the .sql file.
            parse_dates: List of column names to parse as dates.

        Returns:
            A Pandas DataFrame with the results of the query.
        """
        with open(sql_file_path, 'r') as f:
            query = f.read()
            return self.df_from_query(query=query, parse_dates=parse_dates)

    def df_from_table(self, table_name: str, parse_dates: List[str] = None) -> pd.DataFrame:
        """
        Loads a table into a Pandas DataFrame.
        Args:
            table_name: Name of the database table.
            parse_dates: List of column names to parse as dates.

        Returns:
            A Pandas DataFrame consisting of the full table.
        """
        if self.use_cache:
            cache_path = f'{self.cache_directory_path}/{table_name}.hdf'
            if os.path.isfile(cache_path):
                logger.info(f"Cache available: "
                            f"Reading cache for table '{table_name}'...")
                return pd.read_hdf(cache_path)
            else:
                logger.info(f"Cache not available:"
                            f"Reading and caching '{table_name}' from the '{self.database_name}' database...")
                df = pd.read_sql_table(table_name=table_name, con=self.engine, parse_dates=parse_dates)
                df.to_hdf(path_or_buf=cache_path, key='df', format='table')
                return df
        else:
            logger.info(f"Reading '{table_name}' from the '{self.database_name}' database...")
            return pd.read_sql_table(table_name=table_name, con=self.engine, parse_dates=parse_dates)

    def df_to_table(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace', index: bool = False) -> None:
        """
        Inserts a Pandas DataFrame into a database table.
        Args:
            df: The DataFrame to insert into a database table.
            table_name: Name of the database table.
            if_exists: {'fail', 'replace', 'append'} - How to behave if the table already exists.
            index: Write DataFrame index as a column. Uses `index_label` as the column name in the table.
        """
        logger.info(f'Inserting DataFrame into the table {table_name}')
        df.to_sql(name=table_name, con=self.engine, if_exists=if_exists, index=index, chunksize=1000)
