import logging
import os

from airflow.models.baseoperator import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.context import Context
from pandas import DataFrame
from tabulate import tabulate


def create_database_if_not_exists_query(table_name: str):  # TODO parametrize columns from dataframe
    return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                      date DATE PRIMARY KEY,
                      NVDA_close float,
                      NVDA_dif_open_close float,
                      NVDA_range_day float,
                      NVDA_sign_day varchar(1),                      
                      TSLA_close float,
                      TSLA_dif_open_close float,
                      TSLA_range_day float,
                      TSLA_sign_day varchar(1),                       
                      MSFT_close float,
                      MSFT_dif_open_close float,
                      MSFT_range_day float,
                      MSFT_sign_day varchar(1),   
                      AMZN_close float,
                      AMZN_dif_open_close float,
                      AMZN_range_day float,
                      AMZN_sign_day varchar(1),   
                      AMD_close float,
                      AMD_dif_open_close float,
                      AMD_range_day float,
                      AMD_sign_day varchar(1),  
                      INTC_close float,
                      INTC_dif_open_close float,
                      INTC_range_day float,
                      INTC_sign_day varchar(1),                        
                      btc_usd float      
                    )
        """


class PostgresInsertFromDataFrameOperator(BaseOperator):

    def __init__(self,
                 table_name: str,
                 xcom_task_id: str,
                 xcom_task_id_key: str,
                 **kwargs):
        super(PostgresInsertFromDataFrameOperator, self).__init__(**kwargs)
        self.postgres_hook = PostgresHook(postgres_conn_id="postgres_localhost")
        self.table_name = table_name
        self.xcom_task_id = xcom_task_id
        self.xcom_task_id_key = xcom_task_id_key

    def _create_if_table_not_exists(self):
        self.postgres_hook.run(sql=create_database_if_not_exists_query(self.table_name))

    @staticmethod
    def _conflict_with_data(df_rows: DataFrame) -> bool:
        if df_rows.shape[0] != 1 or df_rows.dropna().shape[0] != 1:
            logging.warning("There is a conflict in actualization of data. "
                            "It may not have been traded on NASDAQ that day. "
                            "No data will be inserted in database today.")
            return True
        return False

    def _current_day_data_already_stored(self, current_day: str) -> bool:
        query = f"SELECT btc_usd FROM {self.table_name} WHERE date = '{current_day}';"
        conn = self.postgres_hook.get_conn()
        cursor = conn.cursor()
        cursor.execute(query)
        results = [doc for doc in cursor]
        if len(results) > 0:
            logging.warning(f"There is registered data for day {current_day}. Ignoring insert.")
            return True
        return False

    def execute(self, context: Context):
        task_instance = context['task_instance']
        df_rows = task_instance.xcom_pull(self.xcom_task_id, key=self.xcom_task_id_key)
        if self._conflict_with_data(df_rows):
            return
        self._create_if_table_not_exists()
        if self._current_day_data_already_stored(df_rows.iloc[0]["date"]):
            return
        logging.info("Inserting new data: ")
        logging.info(tabulate(df_rows, headers='keys', tablefmt='psql'))
        df_rows.to_csv("/opt/tmp.csv", index=False, header=False, sep='\t')
        self.postgres_hook.bulk_load(self.table_name, "/opt/tmp.csv")
        os.remove("/opt/tmp.csv")
