"""
Author Hamid, Vakilzadeh PhD
November 2022

"""
import numpy as np
import pandas as pd
import yaml
import streamlit as st
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.sectorperformance import SectorPerformances
import requests
import json
import openai
import openai
import yfinance as yf
from bs4 import BeautifulSoup
import seaborn as sns

secrets = yaml.safe_load(open('secrets.yaml'))
openai.api_key = secrets['openai']

ts = TimeSeries(key=secrets['alpha_vantage'], output_format='pandas')
fd = FundamentalData(key=secrets['alpha_vantage'])
sp = SectorPerformances(key=secrets['alpha_vantage'])

cm = sns.light_palette("seagreen", as_cmap=True)

def find_match(ticker: str = 'AAPL'):
    response = requests.get(url='https://www.alphavantage.co/query',
                                  params={'function': 'SYMBOL_SEARCH',
                                          'keywords': ticker,
                                          'datatype': 'json',
                                          'apikey': secrets['alpha_vantage']}
                 )
    return response.json()


@st.cache_data
def company_overview(ticker: str):
    return fd.get_company_overview(symbol=ticker)

@st.cache_data
def weekly_prices(ticker: str):
    data = ts.get_weekly_adjusted(ticker)[0]
    data.rename(columns={'1. open':'open', '2. high': 'high', '3. low': 'low',
                         '4. close': 'close', '5. adjusted close': 'adjusted close',
                         '6. volume': 'volume', '7. dividend amount': 'dividend amount',
                         '8. split coefficient': 'split coefficient'},
                inplace=True)
    return data

@st.cache_data
def sector_data():
    data = sp.get_sector()
    return data

@st.cache_data
def get_income_statement(ticker: str):
    data = fd.get_income_statement_annual(symbol=ticker)
    data, currency = standardize_data(data[0])
    return data, currency

def standardize_data(database: pd.DataFrame):
    data = database.transpose()
    data.columns = data.iloc[0]
    currency = data.iloc[1,1]
    data.drop(data.index[0:1], inplace=True)
    data.drop(['reportedCurrency'], inplace=True)
    data.replace(to_replace="None", value=0, inplace=True)
    data = data.apply(pd.to_numeric)
    return data ,currency

@st.cache_data
def get_balance_sheet(ticker: str):
    data = fd.get_balance_sheet_annual(symbol=ticker)
    data, currency = standardize_data(data[0])
    return data, currency

@st.cache_data
def get_cash_flow(ticker: str):
    data = fd.get_cash_flow_annual(symbol=ticker)
    data, currency = standardize_data(data[0])
    return data, currency

@st.cache_data
def get_news(ticker: str):
    symbol = yf.Ticker(ticker= ticker)
    return symbol.get_news()


@st.cache_resource
def get_news_text(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    text = soup.find('body')
    return text


def make_pretty(styler):
    styler.set_caption("Weather Conditions")
    styler.format_index(lambda v: v.strftime("%A"))
    styler.background_gradient(axis=None, vmin=1, vmax=5, cmap="YlGnBu")
    return styler


if __name__ == '__main__':
    st.session_state.selected_ticker = st.selectbox(label='Select Ticker',
                                                    options=['AAPL', 'AMZN',
                                                             'META', 'NFLX'])


    st.session_state.company_overview = company_overview(st.session_state.selected_ticker)
    st.session_state.weekly_prices = weekly_prices(st.session_state.selected_ticker)

    st.session_state.balance_sheet, bs_reported_currency = get_balance_sheet(st.session_state.selected_ticker)
    st.session_state.income_statement, is_reported_currency = get_income_statement(st.session_state.selected_ticker)
    st.session_state.cash_flow, cf_reported_currency = get_cash_flow(st.session_state.selected_ticker)

    st.json(st.session_state.company_overview)

    company_info_tab, price_chart_tab, bs_tab, income_tab, cashflow_tab , news_tab = \
        st.tabs(['About the Company', 'Stock Price Chart', 'Balance Sheet',
                 'Income Statement', 'Statement of Cash Flow', 'News'])

    with company_info_tab:
        st.metric(label=st.session_state.company_overview[0]['Name'],
                        value=st.session_state.company_overview[0]['Symbol'])
        st.markdown(st.session_state.company_overview[0]['Description'])

        st.write(st.session_state.company_overview[0]['AssetType'])
    with price_chart_tab:
        st.line_chart(st.session_state.weekly_prices, y='adjusted close')

    with bs_tab:
        df = st.session_state.balance_sheet
        st.metric(label='Currency', value=bs_reported_currency)
        st.checkbox(label='View Balance Sheet')
        st.dataframe(df.style.format(formatter=(lambda x: 'M$ {:,.0f}'.format(x / 1e6)))
                     .background_gradient(cmap=cm)
                 )

        """
        bs1, bs2 = st.columns([2,5])
        with bs1:
            st.session_state.selected_bs_line = st.selectbox(
                'Balance Sheet Line Item',
                options=st.session_state.balance_sheet.columns.tolist()[2:]
            )
        with bs2:
            st.session_state.income_statement['converted'] = \
                pd.to_numeric(st.session_state.income_statement[st.session_state.selected_is_line]) / 1000000
            st.line_chart(data = st.session_state.income_statement,
                          y = 'converted',
                          x = 'fiscalDateEnding')
        """

    with income_tab:
        st.write(st.session_state.income_statement)
        """
        is1, is2 = st.columns([2,5])
        with is1:
            st.session_state.selected_is_line = st.selectbox(
                'Income Statement Line Item',
                options=st.session_state.income_statement.columns.tolist()
            )
        with is2:
            st.session_state.income_statement['converted'] = \
                pd.to_numeric(st.session_state.income_statement[st.session_state.selected_is_line]) / 1000000
            st.line_chart(data = st.session_state.income_statement,
                          y = 'converted',
                          x = 'fiscalDateEnding')"""

    with cashflow_tab:
        st.write(st.session_state.cash_flow)


    with news_tab:
        news = get_news(st.session_state.selected_ticker)
        selected_news = st.selectbox('Select News title to read a summary',
                                     options=[title['title'] for title in news],
                                     )
        st.session_state.selected_news = [url['link'] for url in news if url['title'] == selected_news][0]
        st.write(get_news_text(st.session_state.selected_news))
