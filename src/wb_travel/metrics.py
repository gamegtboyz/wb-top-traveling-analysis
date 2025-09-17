import pandas as pd
import numpy as np
import boto3
from io import StringIO
from airflow.models import Variable

# here we built up the functions that will be used in tests/test_metrics.py
def derived_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.divide(denominator.replace({0: np.nan})).astype("float64")

def derived_divide_pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.divide(denominator.replace({0: np.nan})) * 100.0

# def cagr(series: pd.Series) -> float:
#     """
#     Simple CAGR rate from first to last non-null value in %
#     """
#     s = series.dropna()
    
#     if(len(s) < 2):
#         return np.nan
    
#     start, end = s.iloc[0], s.iloc[-1]
#     if start in (0, None) or pd.isna(start):
#         return np.nan
    
#     periods = len(s) - 1
#     return ((end/start) ** (1/periods) - 1) * 100.0

def ratiofill(fill_df: pd.DataFrame, ref_df: pd.DataFrame) -> pd.DataFrame:
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

def csv_s3_load(df: pd.DataFrame, bucket_name: str, outputs: str):
    """
    Load a DataFrame as a CSV file to an S3 bucket.
    """
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    s3_resource = boto3.resource('s3',
                                 aws_access_key_id=Variable.get("AWS_ACCESS_KEY_ID"),
                                 aws_secret_access_key=Variable.get("AWS_SECRET_ACCESS_KEY"))
    s3_resource.Object(bucket_name, outputs).put(Body=csv_buffer.getvalue())