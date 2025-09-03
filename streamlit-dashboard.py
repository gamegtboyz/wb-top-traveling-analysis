import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events
import pandas as pd
from scipy.stats import gmean

# Page and title configuration
st.set_page_config(page_title="International Tourism Analysis", page_icon='🌏', layout="wide")
st.title("International Tourism Analysis")
# import data into work area
data = pd.read_csv('./data/data.csv')
data.dropna(axis=0,subset=['income_level'],inplace=True)

# add the sidebar for filters
st.sidebar.header('Filters')
# add sidebar elements
selected_countries = st.sidebar.selectbox(label='Country:',
                                          options=data['country_name'].unique(),
                                          index=None,
                                          placeholder='Select Country')

# we need to show the year options in reverse order
selected_year = st.sidebar.selectbox(label='Year:',
                                     options=data['year'].unique()[::-1].tolist())


# create data filtering logic
filtered_amount = data.loc[(data['country_name'] == selected_countries) &\
                           (data['year'] == selected_year)]

# create dashboard component

# first section: value card
st.header('Internaitonal Tourism in Numbers')
st.write('Here is your country\'s tourism summarised in numbers.')

# value card
gdp = filtered_amount['NY.GDP.MKTP.CD'].sum()
receipt = filtered_amount['ST.INT.RCPT.CD'].sum()
arrivals = filtered_amount['ST.INT.ARVL'].sum()
personal_spendings = filtered_amount['rcpt_per_arvl'].sum()
gdp_contribution = filtered_amount['rcpt_per_gdp'].mean()

col1, col2, col3 = st.columns(3)
col1.metric(label='Contry', value=selected_countries)
col2.metric(label='Year', value=selected_year)
col3.metric(label='International Tourism Receipt (Million) (%GDP)', value=f"{(receipt/1000000):,.0f} $ ({(gdp_contribution*100):.2f}% to GDP)")

col4, col5, col6 = st.columns(3)
col4.metric(label='Nominal GDP (Million)', value=f"{(gdp/1000000):,.0f} $")
col5.metric(label='International Tourist Arrivals (Person)', value=f"{arrivals:,.0f}")
col6.metric(label='Spendings per person', value=f"{personal_spendings:,.2f} $")



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

# second part: show the trend analysis of selected country
st.header(f"How does {selected_countries} perform so far?")
st.write(f"Here's how do {selected_countries} performed so far from 2000 to 2020.")

# 1. Receipts performance
fig = px.line(timed_grouped_receipt,
              x='year', y='ST.INT.RCPT.CD')

fig.update_traces(line_color='#44af69')

fig.add_annotation(
    x=timed_grouped_receipt['year'].min() + ((timed_grouped_receipt['year'].max() - timed_grouped_receipt['year'].min())*.15),
    y=timed_grouped_receipt['ST.INT.RCPT.CD'].max()*0.85,
    text=f"Growth rate: ${((gmean(timed_grouped_receipt['pct_change'][1:-1])-1)*100):,.2f}%",
    font=dict(size=24, color="black"),
    align="center",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor="black",
    borderwidth=1,
)

fig.update_layout(title=f"Historical receipt performance",
                  title_subtitle = {
                      'font': {
                          'color': '#FF0000',
                          'style': 'italic'
                          },
                      'text': '2020 is excluded from growth rate calculations'
                  },
                  yaxis={
                      'title':{
                          'text': 'International Tourism Receipt (US Dollars)'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig, use_container_width=True)

# 2. Arrivals performance
fig = px.line(timed_grouped_arrivals,
              x='year', y='ST.INT.ARVL')

fig.update_traces(line_color='#2b9eb3')

fig.add_annotation(
    x=timed_grouped_arrivals['year'].min() + ((timed_grouped_arrivals['year'].max() - timed_grouped_arrivals['year'].min())*.15),
    y=timed_grouped_arrivals['ST.INT.ARVL'].max()*0.85,
    text=f"Growth rate: ${((gmean(timed_grouped_arrivals['pct_change'][1:-1])-1)*100):,.2f}%",
    font=dict(size=24, color="black"),
    align="center",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor="black",
    borderwidth=1,
)

fig.update_layout(title=f"Historical International Tourist Arrivals",
                  title_subtitle = {
                      'font': {
                          'color': '#FF0000',
                          'style': 'italic'
                          },
                      'text': '2020 is excluded from growth rate calculations'
                  },
                  yaxis={
                      'title':{
                          'text': 'International Tourist Arrivals (Person)'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig, use_container_width=True)

# 3. Spendings trends
fig = px.line(timed_grouped_spendings,
              x='year', y='rcpt_per_arvl')

fig.update_traces(line_color='#f1c40f')

fig.add_annotation(
    x=timed_grouped_spendings['year'].min() + ((timed_grouped_spendings['year'].max() - timed_grouped_spendings['year'].min())*.15),
    y=timed_grouped_spendings['rcpt_per_arvl'].max()*0.85,
    text=f"Growth rate: ${((gmean(timed_grouped_spendings['pct_change'][1:-1])-1)*100):,.2f}%",
    font=dict(size=24, color="black"),
    align="center",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor="black",
    borderwidth=1,
)

fig.update_layout(title=f"Historical International Tourist Spendings",
                  title_subtitle = {
                      'font': {
                          'color': '#FF0000',
                          'style': 'italic'
                          },
                      'text': '2020 is excluded from growth rate calculations'
                  },
                  yaxis={
                      'title':{
                          'text': 'International Tourist Arrivals Spendings (US Dollars)'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig, use_container_width=True)

# 4. Historical GDP contributions
fig = px.line(timed_grouped_contributions,
              x='year', y='rcpt_per_gdp')

fig.update_traces(line_color='#d90368')

fig.update_layout(title=f"Historical International Tourist Spendings",
                  yaxis={
                      'title':{
                          'text': 'International Tourist Arrivals Spendings (US Dollars)'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig, use_container_width=True)



# # third part: show top 5 countries of the selected year
st.header(f"Who are the top players in {selected_year}")
st.write(f"This is the top 5 countries in terms of tourist arrivals, tourism receipt, personal spendings, and contribution to GDP.")

# 1. Top5 receipt
fig = px.bar(grouped_receipt[grouped_receipt['year'] == selected_year][0:5][::-1],
             x='ST.INT.RCPT.CD', y='country_name', text='Billions')

fig.update_layout(title=f"Top 5 International Tourism Receipt in {selected_year}",
                  yaxis={
                      'title':{
                          'text': 'Country'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'International Tourism Receipts (Billion US Dollars)'
                      }
                  })

fig.update_traces(marker_color='#44af69')

st.plotly_chart(fig, use_container_width=True)

# 2. Top5 Arrivals
fig = px.bar(grouped_arrivals[grouped_arrivals['year'] == selected_year][0:5][::-1],
             x='ST.INT.ARVL', y='country_name', text='Millions')

fig.update_layout(title=f"Top 5 International Tourist Arrivals in {selected_year}",
                  yaxis={
                      'title':{
                          'text': 'Country'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'International Tourist Arrivals (Person)'
                      }
                  })

fig.update_traces(marker_color='#2b9eb3')

st.plotly_chart(fig, use_container_width=True)

# 3. Top5 Spendings
fig = px.bar(grouped_spendings[grouped_spendings['year'] == selected_year][0:5][::-1],
             x='rcpt_per_arvl', y='country_name', text='Decimals')

fig.update_layout(title=f"Top 5 International Tourist Spendings in {selected_year}",
                  yaxis={
                      'title':{
                          'text': 'Country'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'International Tourist Spendings (US Dollars)'
                      }
                  })

fig.update_traces(marker_color='#f1c40f')

st.plotly_chart(fig, use_container_width=True)

# 3. Top5 GDP contributions
fig = px.bar(grouped_contributions[grouped_contributions['year'] == selected_year][0:5][::-1],
             x='rcpt_per_gdp', y='country_name', text='Percentage')

fig.update_layout(title=f"Top 5 International Tourist Contributions to GDP in {selected_year}",
                  yaxis={
                      'title':{
                          'text': 'Country'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'International Tourist Spendings (US Dollars)'
                      }
                  })

fig.update_traces(marker_color='#d90368')

st.plotly_chart(fig, use_container_width=True)