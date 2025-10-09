import pandas as pd
import numpy as np
from wb_travel.metrics import derived_divide, ratiofill


# test user-defined functions in metrics.py
def test_derived_divide_basic():
    r = pd.Series([1000.0, 2000.0, 0.0])
    a = pd.Series([10.0, 20.0, 5.0])
    output = derived_divide(r, a)
    assert output.tolist() == [100.0, 100.0, 0.0]

def test_derived_divide_div_by_zero_is_nan():
    r = pd.Series([1000.0, 2000.0])
    a = pd.Series([0.0, 10.0])
    output = derived_divide(r, a)
    assert pd.isna(output.iloc[0]) & (output.iloc[1] == 200.0)

# def test_derived_divide_pct():
#     r = pd.Series([50.0, 200.0])
#     g = pd.Series([1000.0, 4000.0])
#     output = derived_divide_pct(r, g)
#     assert output.tolist() == [5.0, 5.0]

# def test_cagr():
#     assert pd.isna(cagr(pd.Series([None, 100.0])))
#     assert pd.isna(cagr(pd.Series([100])))
    
def test_ratiofill(target, reference):
    ratio = reference.iloc[-1, 0] / reference.iloc[-2, 0]
    filled = target.fillna(method='ffill')  
    return pd.DataFrame(filled)
    