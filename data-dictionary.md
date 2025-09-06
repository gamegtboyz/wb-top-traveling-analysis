# Data Dictionary - World Tourism Analysis

**Source**: World Bank Gruop API (wbgapi)\
**Granularity**: Country-Year

## Raw Indicators (Metrics extracted from API)
- **International tourism, receipts (current US$)** -- `ST.INT.RCPT.CD`\
USD value of expenditures made by international inbound visitors.
- **International tourism, number of arrivals** -- `ST.INT.ARVL`\
Count of inbound visitors traveling to a country.
- **GDP (current US$)** -- `NY.GDP.MKTP.CD`\
The nominal value of Gross Domestic Product for a year shown as US Dollars.
- **GDP (current US$)** -- `NY.GDP.PCAP.CD`\
The nominal value of Gross Domestic Product per Capita for a year shown as US Dollars.
- **Population, total** -- `SP.POP.TOTL`\
Total Population in the country
- **Income Level** -- `income_level`\
The collection of countries grouped by GDP per capita

## Derived Metrics (Metrics calculated from Raw Indicators)
- **Receipts per Arrival** -- `rcpt_per_arvl = ST.INT.RCPT.CD / ST.INT.ARVL`\
Average spending per tourist. This amout reflects the purchasing power of the tourists.
- **Receipts per GDP** -- `rcpt_per_gdp = ST.INT.RCPT.CD / NY.GDP.MKTP.CD`\
Portion of international tourist's expenditure compared to the GDP. This shows the dependency of the tourism industry to country's whole GDP.
- **Arrivals per Population** -- `arvl_per_pop = ST.INT.ARVL / SP.POP.TOTL`\
Portion between international tourists compared to country's population.

## Data Quality Notes
- Missing values in `ST.INT.RCPT.CD` and `ST.INT.ARVL` is initially handled using average receipts per arrival of each country. The remaining missing values will be treated as NaN (Not a Number) to handle a possible error due to divide-by-zero.
- Monetary Values are shown in **current USD**, which means the value is shown without inflation-adjusted.
- Country coverage and years vary by indicator.
- Assumed that all data fetched from API is free from material misstatements.

## Transform Flow
1. Pull row indicators via World Bank Group API.
2. Normalized column names, ensure numeric types, handle missing value safely.
3. Compute derived metrics.
4. Persisted processed tables for dashboard.