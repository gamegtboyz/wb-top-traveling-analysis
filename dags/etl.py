import wbgapi as wb
import pandas as pd

def extract():
    """
    Extracts data from the World Bank Global Findex database, then load it into a csv file
    """
    selected_indicators = [
        'NY.GDP.MKTP.CD',   # GDP (current US$)
        'ST.INT.RCPT.CD',   # International tourism, receipts (current US$)
        'ST.INT.ARVL',      # International tourism, number of arrivals
        'SP.POP.TOTL'       # Population, total
    ]

    selected_countries = ['USA','MEX','FRA','ITA','JPN','THA']

    period = range(2000, 2021)  # 2000 to 2020

    # Fetch data from the World Bank API
    data = wb.get_dataframe(
        selected_indicators,
        selected_countries,
        time=period
    )
    return data


def transform(data):
    """
    Transforms the extracted data by filling missing values and calculating ratios.
    """
    for country in data.index.levels[0]:
        data.loc[[(country, 'ST.INT.ARVL')]] = ratiofill(
            data.loc[[(country, 'ST.INT.ARVL')]],
            data.loc[[(country, 'ST.INT.RCPT.CD')]]
        )

        data.loc[[(country, 'ST.INT.RCPT.CD')]] = ratiofill(
            data.loc[[(country, 'ST.INT.RCPT.CD')]],
            data.loc[[(country, 'ST.INT.ARVL')]]
        )
    return data


def load_csv(data, filename='data.csv'):
    """
    Loads the data into a CSV file.
    """
    data.to_csv(filename, index=True)
    print(f"Data loaded into {filename}")


def ratiofill(fill_df, ref_df):
    """
    fill missing values in fill_df using the ratio of ref_df
    The ratio is calculated as the mean of the values in ref_df
    for each year, and then applied to fill_df.
    """

    # find the ratio of the reference dataframe
    ratio = fill_df.mean(axis=1).values[0]/ref_df.mean(axis=1).values[0]

    # find and fill the NaN values
    for column in fill_df.columns:
        if fill_df[column].isna().values[0]:
            fill_df[column].values[0] = ref_df[column].values[0] * ratio

    return fill_df.values