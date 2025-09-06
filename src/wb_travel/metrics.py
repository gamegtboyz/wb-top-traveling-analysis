import pandas as pd
import numpy as np

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

def ratiofill(target: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in target DataFrame using the ratio of the mean of target to the mean of reference.
    """
    target_mean = target.mean().values[0]
    reference_mean = reference.mean().values[0]
    
    if pd.isna(target_mean) or pd.isna(reference_mean) or reference_mean == 0:
        return target
    
    ratio = target_mean / reference_mean
    filled_values = reference * ratio
    filled_values[target.notna()] = target[target.notna()]
    
    return filled_values