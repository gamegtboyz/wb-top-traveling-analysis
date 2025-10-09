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
    # Create input DataFrames
    fill_df = pd.DataFrame({0: [np.nan, 200.0, np.nan, 400.0, np.nan]})
    ref_df = pd.DataFrame({0: [10.0, 20.0, 30.0, 40.0, 50.0]})

    # Run the function
    output = ratiofill(fill_df.copy(), ref_df)

    # Expected ratio
    ratio = np.nanmean(fill_df[0]) / np.mean(ref_df[0])
    # Expected filled values
    expected = fill_df.copy()
    expected[0] = expected[0].fillna(ref_df[0] * ratio)
    expected_array = expected.values

    # Compare results
    assert np.allclose(output, expected_array)
    