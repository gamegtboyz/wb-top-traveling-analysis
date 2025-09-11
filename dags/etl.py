import wbgapi as wb
import pandas as pd
#from sqlalchemy import create_engine
#from config.dbconfig import connection_string
#from src.wb_travel.metrics import ratiofill, derived_divide, derived_divide_pct
from metrics import ratiofill, derived_divide, derived_divide_pct, csv_s3_load
from airflow.models import Variable

def extract_transform_load():
    """
    Extracts data from the World Bank Global Findex database, then load it into a csv file
    """
    selected_indicators = [
        'NY.GDP.MKTP.CD',   # GDP (current US$)
        'ST.INT.RCPT.CD',   # International tourism, receipts (current US$)
        'ST.INT.ARVL',      # International tourism, number of arrivals
        'SP.POP.TOTL',      # Population, total
        'NY.GDP.PCAP.CD'    # GDP per capita (current US$)
    ]

    period = range(2000, 2021)  # 2000 to 2020

    global data

    # Fetch data from the World Bank API
    data = wb.data.DataFrame(
        selected_indicators,
        time=period
    )

    # fetch country map data
    country_map = wb.economy.DataFrame().reset_index()
    country_map = country_map[['id', 'name', 'incomeLevel']]

    # transform the data
    for country in data.index.levels[0]:
        data.loc[[(country, 'ST.INT.ARVL')]] = ratiofill(
            data.loc[[(country, 'ST.INT.ARVL')]],
            data.loc[[(country, 'ST.INT.RCPT.CD')]]
        )

        data.loc[[(country, 'ST.INT.RCPT.CD')]] = ratiofill(
            data.loc[[(country, 'ST.INT.RCPT.CD')]],
            data.loc[[(country, 'ST.INT.ARVL')]]
        )

    # reset the index
    data.reset_index(inplace=True)

    # melt to rename the series of year value
    data = data.melt(id_vars=['economy', 'series'],
                     var_name='year',
                     value_name='value')
    data['year'] = data['year'].str.replace('YR', '').astype(int)

    # pivot the data
    data = data.pivot_table(
        index=['economy', 'year'],
        columns='series',
        values='value'
    ).reset_index()

    # add the calculated column
    data['rcpt_per_arvl'] = derived_divide(data['ST.INT.RCPT.CD'], data['ST.INT.ARVL'])
    data['rcpt_per_gdp'] = derived_divide_pct(data['ST.INT.RCPT.CD'], data['NY.GDP.MKTP.CD'])
    data['arvl_per_pop'] = derived_divide(data['ST.INT.ARVL'], data['SP.POP.TOTL'])

    # join the country with the name and income level
    data = data.merge(country_map, left_on='economy', right_on='id', how='left')
    data.drop(columns='id',axis=1,inplace=True)
    data.dropna(axis=0,subset=['incomeLevel'],inplace=True)

    # rename the columns
    data.rename(columns={
        'economy': 'country_code',
        'name': 'country_name',
        'incomeLevel': 'income_level',
        'series': 'indicator'
    }, inplace=True)

    # Load the data into a CSV file in S3 bucket
    try:
        csv_s3_load(data, bucket_name=Variable.get("S3_BUCKET_NAME"), outputs='data/data.csv')
        print("data extracted and transformed successfully.")
    except Exception as e:
        print(f"An error occurred while saving data to CSV: {e}")

    # # Load the data into a SQL database
    # engine = create_engine(connection_string)

    # table_name = 'world_travel_data'

    # try:
    #     data.to_sql(table_name, engine, if_exists='replace', index=True)
    #     print(f"data loaded into {table_name} table in the database successfully.")
    # except Exception as e:
    #     print(f"An error occurred while loading data into the database: {e}")

    # engine.dispose()

# We moved this function to src/wb_travel/metrics.py
# def ratiofill(fill_df, ref_df):
#     """
#     fill missing values in fill_df using the ratio of ref_df
#     The ratio is calculated as the mean of the values in ref_df
#     for each year, and then applied to fill_df.
#     """

#     # find the ratio of the reference dataframe
#     ratio = fill_df.mean(axis=1).values[0]/ref_df.mean(axis=1).values[0]

#     # find and fill the NaN values
#     for column in fill_df.columns:
#         if fill_df[column].isna().values[0]:
#             fill_df[column].values[0] = ref_df[column].values[0] * ratio

#     return fill_df.values