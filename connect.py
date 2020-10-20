import psycopg2
import pandas as pd
from config import config


class Connect:
    def __init__(self, params=config()):
        # Initialise database connection and cursor with config.py parameters
        self.conn = psycopg2.connect(**params)
        self.cur = self.conn.cursor()

    def get_table_with_query(self, query):
        # Execute string as SQL query and return data into pandas df
        self.cur.execute(query)
        col_names = [desc[0] for desc in self.cur.description]
        data = self.cur.fetchall()
        return pd.DataFrame(data, columns=col_names)

    def write_data_to_table(self, query):
        # Execute a write command to the postgres database
        self.cur.execute(query)
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Automatically close connection and cursor at the end of with block
        self.cur.close()
        self.conn.close()
