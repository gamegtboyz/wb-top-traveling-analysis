# download the relevant library
from sqlalchemy import create_engine
import pandas as pd
from config.dbconfig import connection_string

def query_to_csv():
    # create database connection
    engine = create_engine(connection_string)

    # create SQL query
    query = "SELECT * FROM world_travel_data"

    # read the query, then export to csv files
    pd.read_sql_query(query, engine).to_csv('./data/data.csv')

    # create SQL query
    selected_query = "SELECT " \
    "country_code, country_name, year, 'NY.GDP.MKTP.CD' AS GDP, rcpt_per_gdp, 'ST.INT.ARVL' AS Arrivals, 'ST.INT.RCPT.CD' AS Receipt, rcpt_per_arvl " \
    "FROM world_travel_data"

    # read the query, then export to csv files
    pd.read_sql_query(selected_query, engine).to_csv('./data/extracted_query.csv')

    # close database connection
    engine.dispose()