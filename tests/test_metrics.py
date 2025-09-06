import pandas as pd
from wb_travel.metrics import derived_divide, derived_divide_pct, ratiofill


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

def test_derived_divide_pct():
    r = pd.Series([50.0, 200.0])
    g = pd.Series([1000.0, 4000.0])
    output = derived_divide_pct(r, g)
    assert output.tolist() == [5.0, 5.0]

# def test_cagr():
#     assert pd.isna(cagr(pd.Series([None, 100.0])))
#     assert pd.isna(cagr(pd.Series([100])))
    
def test_ratiofill():
    target = pd.DataFrame({0: [None, 200.0, None, 400.0, None]})
    reference = pd.DataFrame({0: [10.0, 20.0, 30.0, 40.0, 50.0]})
    output = ratiofill(target, reference)
    expected = pd.DataFrame({0: [100.0, 200.0, 300.0, 400.0, 500.0]})
    assert output.equals(expected)
    