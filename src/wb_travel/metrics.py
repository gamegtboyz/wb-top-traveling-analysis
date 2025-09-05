import pandas as pd
import numpy as np

# here we built up the functions that will be used in tests/test_metrics.py
def receipts_per_arrival(receipts_usd: pd.Series, arrivals: pd.Series) -> pd.Series:
    return receipts_usd.divide(arrivals.replace({0: np.nan})).astype("float64")

def receipts_per_gdp(receipts_usd: pd.Series, gdp: pd.Series) -> pd.Series:
    return receipts_usd.divide(gdp.replace({0: np.nan})) * 100.0

def arrivals_per_pop(arrivals: pd.Series, population: pd.Series) -> pd.Series:
    return arrivals.divide(population.replace({0: np.nan})).astype("float64")

def cagr(series: pd.Series) -> float:
    """
    Simple CAGR rate from first to last non-null value in %
    """
    s = series.dropna()
    
    if(len(s) < 2):
        return np.nan
    
    start, end = s.iloc[0], s.iloc[-1]
    if start in (0, None) or pd.isna(start):
        return np.nan
    
    periods = len(s) - 1
    return ((end/start) ** (1/periods) - 1) * 100.0