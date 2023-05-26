"""
Author Hamid, Vakilzadeh PhD
March 2023

"""
# importing libraries
import pandas as pd
import yaml
import streamlit as st
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
import requests
import seaborn as sns
from tabs import (company_info,
                  company_price_chart,
                  company_balance_sheet,
                  company_income_statement,
                  company_cash_flow,
                  company_news)


# load secrets
secrets = yaml.safe_load(open('secrets.yaml'))


# Initialize FundamentalData, SectorPerformances, and TechIndicators objects using your Alpha Vantage API key
fd = FundamentalData(key=secrets['alpha_vantage'])
sp = SectorPerformances(key=secrets['alpha_vantage'])
ti = TechIndicators(key=secrets['alpha_vantage'])


# Set up a seaborn color palette
cm = sns.light_palette("seagreen", as_cmap=True)


# Function to search for a given ticker on Alpha Vantage
def find_match(ticker: str = 'AAPL'):
    response = requests.get(url='https://www.alphavantage.co/query',
                                  params={'function': 'SYMBOL_SEARCH',
                                          'keywords': ticker,
                                          'datatype': 'json',
                                          'apikey': secrets['alpha_vantage']}
                 )
    # Return the JSON response
    return response.json()


# Use Streamlit's cache decorator to store the result of this function, so it only runs once
@st.cache_data
def company_overview(ticker: str):
    # This function gets the company overview for a given ticker
    return fd.get_company_overview(symbol=ticker)


# Use Streamlit's cache decorator to store the result of this function, so it only runs once
@st.cache_data
def sector_data():
    # This function gets sector performance data
    data = sp.get_sector()
    return data


# Use Streamlit's cache decorator to store the result of this function, so it only runs once
@st.cache_data
def get_income_statement(ticker: str):
    # This function gets the annual income statement for a given ticker and standardizes the data
    data = fd.get_income_statement_annual(symbol=ticker)
    data, currency = standardize_data(data[0])
    return data, currency


def standardize_data(database: pd.DataFrame):
    # Function to standardize a DataFrame returned by Alpha Vantage
    data = database.transpose()
    data.columns = data.iloc[0]
    currency = data.iloc[1,1]
    data.drop(data.index[0:1], inplace=True)
    data.drop(['reportedCurrency'], inplace=True)
    data.replace(to_replace="None", value=0, inplace=True)
    data = data.apply(pd.to_numeric)
    data = data.apply(lambda x: x/1000000)  # convert data to millions
    return data ,currency


# Use Streamlit's cache decorator to store the result of this function, so it only runs once
@st.cache_data
def get_balance_sheet(ticker: str):
    # This function gets the annual balance sheet for a given ticker and standardizes the data
    data = fd.get_balance_sheet_annual(symbol=ticker)
    data, currency = standardize_data(data[0])
    return data, currency


# Use Streamlit's cache decorator to store the result of this function, so it only runs once
# This function gets the annual cash flow statement for a given ticker and standardizes the data
@st.cache_data
def get_cash_flow(ticker: str):
    data = fd.get_cash_flow_annual(symbol=ticker)
    data, currency = standardize_data(data[0])
    return data, currency


# Function to format a DataFrame for pretty printing
def make_pretty(styler):
    styler.format(formatter=(lambda x: 'M$ {:,.0f}'.format(x))).background_gradient(cmap=cm)
    return styler


# check if the script is running in the main scope
if __name__ == '__main__':

    # configure Streamlit page properties (title, icon, and layout)
    st.set_page_config(page_title='Financial Statement Analysis', page_icon='📈', layout='centered')

    # create a dropdown menu for selecting ticker with default options as 'AAPL', 'AMZN', 'META', 'NFLX'
    st.session_state.selected_ticker = st.selectbox(label='Select Ticker',
                                                    options=['AAPL', 'AMZN',
                                                             'META', 'NFLX'])

    # fetch and store the company overview details for the selected ticker
    st.session_state.company_overview = company_overview(st.session_state.selected_ticker)

    # fetch and store the balance sheet for the selected ticker and its reported currency
    st.session_state.balance_sheet, bs_reported_currency = get_balance_sheet(st.session_state.selected_ticker)

    # fetch and store the income statement for the selected ticker and its reported currency
    st.session_state.income_statement, is_reported_currency = get_income_statement(st.session_state.selected_ticker)

    # fetch and store the cash flow for the selected ticker and its reported currency
    st.session_state.cash_flow, cf_reported_currency = get_cash_flow(st.session_state.selected_ticker)

    # create a tab layout in Streamlit with the following tabs:
    # 'About the Company', 'Stock Price Chart', 'Balance Sheet', 'Income Statement', 'Statement of Cash Flow', and 'News'
    # each tab is assigned to a corresponding variable for future reference
    company_info_tab, price_chart_tab, bs_tab, income_tab, cashflow_tab, news_tab = \
        st.tabs(['About the Company', 'Stock Price Chart', 'Balance Sheet',
                 'Income Statement', 'Statement of Cash Flow', 'News'])

    # inside the 'About the Company' tab
    with company_info_tab:
        # display company info by
        # calling the function company_info with the first element of the company overview details stored in the session state
        company_info(company_detail=st.session_state.company_overview[0])

    # inside the 'Stock Price Chart' tab
    with price_chart_tab:
        # display a line chart with the weekly prices (adjusted close) of the selected company
        # by calling the function 'company_price_chart' with the selected ticker
        company_price_chart()

    # inside the 'Balance Sheet' tab
    with bs_tab:
        # display the balance sheet by
        # calling the 'company_balance_sheet' function with 'make_pretty' as the formatter function and
        # 'bs_reported_currency' as the reported currency
        company_balance_sheet(formatter=make_pretty, currency=bs_reported_currency)

    # inside the 'Income Statement' tab
    with income_tab:
        # display the income statement by
        # calling the 'company_income_statement' function with 'make_pretty' as the formatter function and
        # 'is_reported_currency' as the reported currency
        company_income_statement(formatter=make_pretty, currency=is_reported_currency)

    # inside the 'Statement of Cash Flow' tab
    with cashflow_tab:
        # display the cash flow by
        # calling the 'company_cash_flow' function with 'make_pretty' as the formatter function and
        # 'cf_reported_currency' as the reported currency
        company_cash_flow(formatter=make_pretty, currency=cf_reported_currency)

    with news_tab:
        # display the latest news about the company by
        # calling the 'company_news' function with the first element of the company overview details stored in the session state
        company_news(ticker=st.session_state.selected_ticker)