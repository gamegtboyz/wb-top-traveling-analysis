import pandas as pd
from scipy.stats import gmean
from streamlit_dashboard import filtered_amount, selected_countries, selected_year

# import data into work area
data = pd.read_csv('./data/data.csv')
data.dropna(axis=0,subset=['income_level'],inplace=True)

# value card
gdp = filtered_amount['NY.GDP.MKTP.CD'].sum()
receipt = filtered_amount['ST.INT.RCPT.CD'].sum()
arrivals = filtered_amount['ST.INT.ARVL'].sum()
personal_spendings = filtered_amount['rcpt_per_arvl'].sum()
gdp_contribution = filtered_amount['rcpt_per_gdp'].mean()

# the grouped data 
grouped_receipt = data.groupby(['country_name','year'])[['ST.INT.RCPT.CD']].sum().sort_values(by='ST.INT.RCPT.CD',ascending=False).reset_index()
grouped_arrivals = data.groupby(['country_name','year'])[['ST.INT.ARVL']].sum().sort_values(by='ST.INT.ARVL',ascending=False).reset_index()
grouped_spendings = data.groupby(['country_name','year'])[['rcpt_per_arvl']].sum().sort_values(by='rcpt_per_arvl',ascending=False).reset_index()
grouped_contributions = data.groupby(['country_name','year'])[['rcpt_per_gdp']].sum().sort_values(by='rcpt_per_gdp',ascending=False).reset_index()

# magnage the unit display
grouped_receipt['Billions'] = (grouped_receipt['ST.INT.RCPT.CD']/1000000000).map("{:,.2f} B".format)
grouped_arrivals['Millions'] = (grouped_arrivals['ST.INT.ARVL']/1000000).map("{:,.0f} M".format)
grouped_spendings['Decimals'] = grouped_spendings['rcpt_per_arvl'].map("$ {:,.2f}".format)
grouped_contributions['Percentage'] = (grouped_contributions['rcpt_per_gdp']*100).map("{:.2f}%".format)

# calculate the value change
timed_grouped_receipt = grouped_receipt[(grouped_receipt['country_name'] == selected_countries)].sort_values(by='year')
timed_grouped_receipt['last_period'] = timed_grouped_receipt['ST.INT.RCPT.CD'].shift(1)
timed_grouped_receipt['pct_change'] = timed_grouped_receipt['ST.INT.RCPT.CD']/timed_grouped_receipt['last_period']

timed_grouped_arrivals = grouped_arrivals[(grouped_arrivals['country_name'] == selected_countries)].sort_values(by='year')
timed_grouped_arrivals['last_period'] = timed_grouped_arrivals['ST.INT.ARVL'].shift(1)
timed_grouped_arrivals['pct_change'] = timed_grouped_arrivals['ST.INT.ARVL']/timed_grouped_arrivals['last_period']

timed_grouped_spendings = grouped_spendings[(grouped_spendings['country_name'] == selected_countries)].sort_values(by='year')
timed_grouped_spendings['last_period'] = timed_grouped_spendings['rcpt_per_arvl'].shift(1)
timed_grouped_spendings['pct_change'] = timed_grouped_spendings['rcpt_per_arvl']/timed_grouped_spendings['last_period']

timed_grouped_contributions = grouped_contributions[(grouped_contributions['country_name'] == selected_countries)].sort_values(by='year')