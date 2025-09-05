import pandas as pd
from src.wb_travel.metrics import receipts_per_arrival, receipts_per_gdp, arrivals_per_pop, cagr


# test the 
def test_receipts_per_arrival_basic():
    r = pd.Series([1000.0, 2000.0, 0.0])
    a = pd.Series([10.0, 20.0, 5.0])
    output = receipts_per_arrival(r, a)
    assert output.tolist() == [100.0, 100.0, 0.0]

def test_receipts_per_arrival_div_by_zero_is_nan():
    r = pd.Series([1000.0, 2000.0])
    a = pd.Series([0.0, 10.0])
    output = receipts_per_arrival(r, a)
    assert pd.isna(output.iloc[0]) & output.iloc[1] == 200.0

def test_receipts_per_gdp():
    r = pd.Series([50.0, 200.0])
    g = pd.Series([1000.0, 4000.0])
    output = receipts_per_gdp(r, g)
    assert output.tolist() == [5.0, 5.0]

def test_arrivals_per_pop():
    a = pd.Series([10000.0, 2000.0])
    p = pd.Series([100.0, 0])
    output = arrivals_per_pop(a, p)
    assert output.iloc[0] == 100.0 & pd.isna(output.iloc[1])

def test_cagr():
    assert pd.isna(cagr(pd.Series([None, 100.0])))
    assert pd.isna(cagr(pd.Series([100])))
    
    