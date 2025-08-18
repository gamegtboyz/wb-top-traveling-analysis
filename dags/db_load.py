import pandas as pd
from sqlalchemy import create_engine
from config.dbconfig import connection_string

def load_sql():
    data = pd.read_csv('./data.csv')

    engine = create_engine(connection_string)

    table_name = 'world_travel_data'

    try:
        data.to_sql(table_name, engine, if_exists='replace', index=True)
        print(f"data loaded into {table_name} table in the database successfully.")
    except Exception as e:
        print(f"An error occurred while loading data into the database: {e}")

    engine.dispose()