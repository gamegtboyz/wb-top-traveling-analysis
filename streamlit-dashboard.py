import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events
import pandas as pd

# Page and title configuration
st.set_page_config(page_title="International Tourism Analysis", page_icon='🌏', layout="wide")
st.title("International Tourism Analysis (2000 - 2020)")

# import data into work area
data = pd.read_csv('./data/data.csv')
data.dropna(axis=0,subset=['income_level'],inplace=True)

# add the sidebar for filters
st.sidebar.header('Filters')
# add sidebar elements
selected_countries = st.sidebar.selectbox(label='Country:',
                                          options=data['country_name'].unique())

# we need to show the year options in reverse order
selected_year = st.sidebar.selectbox(label='Year:',
                                     options=data['year'].unique()[::-1].tolist())


# create data filtering logic
filtered_amount = data.loc[(data['country_name'] == selected_countries) &\
                           (data['year'] == selected_year)]

# create dashboard component
# value card
gdp = filtered_amount['NY.GDP.MKTP.CD'].sum()
receipt = filtered_amount['ST.INT.RCPT.CD'].sum()
arrivals = filtered_amount['ST.INT.ARVL'].sum()
personal_spendings = filtered_amount['rcpt_per_arvl'].sum()
gdp_contribution = filtered_amount['rcpt_per_gdp'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric(label='Nominal GDP (Million)', value=f"{(gdp/1000000):,.0f} $")
col2.metric(label='International Tourist Arrivals (Person)', value=f"{arrivals:,.0f}")
col3.metric(label='International Tourism Receipt (Million)(%gdp)', value=f"{(receipt/1000000):,.0f} $ ({(gdp_contribution*100):.2f}%)")
col4.metric(label='Spendings per person', value=f"{personal_spendings:,.2f} $")

# interactive map
fig = px.choropleth(data,
                    locations='country_name',
                    locationmode='country names',
                    color_continuous_scale='Blues')

# add click events
selected_map = plotly_events(fig)

if selected_map:
    # Get index of the clicked point
    idx = selected_map[0]["pointNumber"]
    
    # Lookup the row in the dataframe
    selected_country = data.iloc[idx]
    
    st.write("You clicked:", selected_country["country_name"])
    selected_countries = selected_country["country_name"]
