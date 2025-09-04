import streamlit as st
import plotly.express as px
import pandas as pd
from scipy.stats import gmean
import os
from huggingface_hub import InferenceClient, login

# import data into work area
data = pd.read_csv('./data/data.csv')
data.dropna(axis=0,subset=['income_level'],inplace=True)

# add sidebar to filter an amount
st.sidebar.header('Filters')
selected_countries = st.sidebar.selectbox(label='Country:',
                                          options=data['country_name'].unique(),
                                          index=None,
                                          placeholder='Select Country')

selected_year = st.sidebar.selectbox(label='Year:',
                                     options=data['year'].unique()[::-1].tolist(),  # sort the list in reverse order
                                     index=None,
                                     placeholder='Select Year')

filtered_amount = data.loc[(data['country_name'] == selected_countries) &\
                           (data['year'] == selected_year)]

# prepare the data
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

hf_token = os.getenv("HF_TOKEN")
login(hf_token)

# load the models here
model_id = "meta-llama/Llama-3.1-8B-Instruct"
client = InferenceClient(model_id)

def llama3_write(data, prompt, max_tokens=400):
    data_prompt = data.to_string(index=False) 
    response = client.chat_completion(
        messages=[{
            'role': 'user',
            'content': f"With {data_prompt} as source data, {prompt}"
        }],
        max_tokens=max_tokens,
        temperature=0.7
    )
    message = response.choices[0].message.content

    return message

# Page and title configuration
st.set_page_config(page_title="International Tourism Analysis", page_icon='🌏', layout="wide")
st.title("International Tourism Analysis")

# create dashboard component
# first section: value card
st.header('Internaitonal Tourism in Numbers')

col1, col2, col3 = st.columns(3)
col1.metric(label='Contry', value=selected_countries)
col2.metric(label='Year', value=selected_year)
col3.metric(label='International Tourism Receipt (Million USD) (%GDP)', value=f"{(receipt/1000000):,.0f} M$ ({(gdp_contribution*100):.2f}% to GDP)")

col4, col5, col6 = st.columns(3)
col4.metric(label='Nominal GDP (Bilion USD)', value=f"{(gdp/1000000):,.0f} B$")
col5.metric(label='International Tourist Arrivals (Person)', value=f"{arrivals:,.0f}")
col6.metric(label='Spendings per person', value=f"{personal_spendings:,.2f} $")



# second section: trend analysis of selected country
st.header(f"How does {selected_countries} perform so far from 2000 to 2020?")

if selected_countries:
    st.write(llama3_write(timed_grouped_receipt, f'How does the International tourism of {selected_countries} goes for the last 20 years from 2000 to 2020? Could you write the narratives as the professional economist without showing a single line of code? Please make it conclusive under your max_tokens credit.'))
else:
    st.write('*[Please select country]*')

# 2.1 Receipts Trend
fig2_1 = px.line(timed_grouped_receipt,
              x='year', y='ST.INT.RCPT.CD')

fig2_1.update_traces(line_color='#44af69')

fig2_1.add_annotation(
    x=timed_grouped_receipt['year'].min() + ((timed_grouped_receipt['year'].max() - timed_grouped_receipt['year'].min())*.15),
    y=timed_grouped_receipt['ST.INT.RCPT.CD'].max()*0.85,
    text=f"Growth rate: ${((gmean(timed_grouped_receipt['pct_change'][1:-1])-1)*100):,.2f}%",
    font=dict(size=24, color="black"),
    align="center",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor="black",
    borderwidth=1,
)

fig2_1.update_layout(title=f"Historical International Tourism Receipt performance",
                  title_subtitle = {
                      'font': {
                          'color': '#FF0000',
                          'style': 'italic'
                          },
                      'text': '2020 is excluded from growth rate calculations due to abnormal changes from COVID-19 pandemic'
                  },
                  yaxis={
                      'title':{
                          'text': 'Int\'l Tourism Receipt (US Dollars)'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig2_1, use_container_width=True)

# 2.2 Arrivals Trend
fig2_2 = px.line(timed_grouped_arrivals,
              x='year', y='ST.INT.ARVL')

fig2_2.update_traces(line_color='#2b9eb3')

fig2_2.add_annotation(
    x=timed_grouped_arrivals['year'].min() + ((timed_grouped_arrivals['year'].max() - timed_grouped_arrivals['year'].min())*.15),
    y=timed_grouped_arrivals['ST.INT.ARVL'].max()*0.85,
    text=f"Growth rate: ${((gmean(timed_grouped_arrivals['pct_change'][1:-1])-1)*100):,.2f}%",
    font=dict(size=24, color="black"),
    align="center",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor="black",
    borderwidth=1,
)

fig2_2.update_layout(title=f"Historical International Tourist Arrivals",
                  title_subtitle = {
                      'font': {
                          'color': '#FF0000',
                          'style': 'italic'
                          },
                      'text': '2020 is excluded from growth rate calculations due to abnormal changes from COVID-19 pandemic'
                  },
                  yaxis={
                      'title':{
                          'text': 'Int\'l Tourist Arrivals (Person)'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig2_2, use_container_width=True)

# 2.3 Spendings Trends
fig2_3 = px.line(timed_grouped_spendings,
              x='year', y='rcpt_per_arvl')

fig2_3.update_traces(line_color='#f1c40f')

fig2_3.add_annotation(
    x=timed_grouped_spendings['year'].min() + ((timed_grouped_spendings['year'].max() - timed_grouped_spendings['year'].min())*.15),
    y=timed_grouped_spendings['rcpt_per_arvl'].max()*0.85,
    text=f"Growth rate: ${((gmean(timed_grouped_spendings['pct_change'][1:-1])-1)*100):,.2f}%",
    font=dict(size=24, color="black"),
    align="center",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor="black",
    borderwidth=1,
)

fig2_3.update_layout(title=f"Historical International Tourist Spendings",
                  title_subtitle = {
                      'font': {
                          'color': '#FF0000',
                          'style': 'italic'
                          },
                      'text': '2020 is excluded from growth rate calculations due to abnormal changes from COVID-19 pandemic'
                  },
                  yaxis={
                      'title':{
                          'text': 'Int\'l Tourist Spendings (US Dollars)'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig2_3, use_container_width=True)

# 2.4 GDP Contributions Trends
fig2_4 = px.line(timed_grouped_contributions,
              x='year', y='rcpt_per_gdp')

fig2_4.update_traces(line_color='#d90368')

fig2_4.update_layout(title=f"Historical International Receipts Contribution to GDP",
                  yaxis={
                      'title':{
                          'text': 'GDP Contributions'
                      }
                  },
                  xaxis={
                      'title':{
                          'text': 'Year'
                      }
                  })

st.plotly_chart(fig2_4, use_container_width=True)



# third section: Top 5 countries for the selected year
st.header(f"Who are the top players in {selected_year}")
if selected_year:
    st.write(llama3_write(grouped_receipt[grouped_receipt['year'] == selected_year][0:5][::-1], f"could you write a narrative to summarize the data focusing on comparison between the country with highest values and the others. Then give us a brief reason how they get the first position in international tourism industry in {selected_year} based on the external sources. Do it like professional economist and make it conclusive within given number of tokens."))
else:
    st.write("*[Please select year]*")

# 3.1 Top5 Receipt
fig3_1 = px.bar(grouped_receipt[grouped_receipt['year'] == selected_year][0:5][::-1],
             x='ST.INT.RCPT.CD', y='country_name', text='Billions')

fig3_1.update_layout(title=f"Top 5 International Tourism Receipt in {selected_year}",
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

fig3_1.update_traces(marker_color='#44af69')

# 3.2 Top5 Arrivals
fig3_2 = px.bar(grouped_arrivals[grouped_arrivals['year'] == selected_year][0:5][::-1],
             x='ST.INT.ARVL', y='country_name', text='Millions')

fig3_2.update_layout(title=f"Top 5 International Tourist Arrivals in {selected_year}",
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

fig3_2.update_traces(marker_color='#2b9eb3')

col7, col8 = st.columns(2)
with col7:
    st.plotly_chart(fig3_1, use_container_width=True)
with col8:
    st.plotly_chart(fig3_2, use_container_width=True)

# 3.3 Top5 Spendings
fig3_3 = px.bar(grouped_spendings[grouped_spendings['year'] == selected_year][0:5][::-1],
             x='rcpt_per_arvl', y='country_name', text='Decimals')

fig3_3.update_layout(title=f"Top 5 International Tourist Spendings in {selected_year}",
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

fig3_3.update_traces(marker_color='#f1c40f')

# 3.4 Top5 GDP contributions
fig3_4 = px.bar(grouped_contributions[grouped_contributions['year'] == selected_year][0:5][::-1],
             x='rcpt_per_gdp', y='country_name', text='Percentage')

fig3_4.update_layout(title=f"Top 5 International Tourist Contributions to GDP in {selected_year}",
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

fig3_4.update_traces(marker_color='#d90368')

col9, col10 = st.columns(2)
with col9:
    st.plotly_chart(fig3_3, use_container_width=True)
with col10:
    st.plotly_chart(fig3_4, use_container_width=True)