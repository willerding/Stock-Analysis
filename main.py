"""
Author Hamid, Vakilzadeh PhD
March 2023

"""
import pandas as pd
import yaml
import streamlit as st
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
import requests
import openai
import yfinance as yf
from bs4 import BeautifulSoup
import seaborn as sns

secrets = yaml.safe_load(open('secrets.yaml'))

openai.api_key = secrets['openai']
ts = TimeSeries(key=secrets['alpha_vantage'], output_format='pandas')
fd = FundamentalData(key=secrets['alpha_vantage'])
sp = SectorPerformances(key=secrets['alpha_vantage'])
ti = TechIndicators(key=secrets['alpha_vantage'])

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
    data = data.apply(lambda x: x/1000000)
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


@st.cache_data
def get_news_text(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='lxml')
    text = soup.find('div', attrs={'class': 'caas-body'}).text
    return text


@st.cache_data
def get_news_summary(text: str, ticker: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello!"},
            {"role": "user", "content": "Please summarize the news article briefly. Also highlight the parts "
                                        f"thar talk about {ticker}"
             },
            {"role": "user", "content": f"{text}"}
        ]
    )
    return response['choices'][0]['message']['content']


def make_pretty(styler):
    styler.format(formatter=(lambda x: 'M$ {:,.0f}'.format(x))).background_gradient(cmap=cm)
    return styler


if __name__ == '__main__':
    st.set_page_config(page_title= 'Financial Statement Anaylysis', page_icon='📈', layout='centered')
    st.session_state.selected_ticker = st.selectbox(label='Select Ticker',
                                                    options=['AAPL', 'AMZN',
                                                             'META', 'NFLX'])


    st.session_state.company_overview = company_overview(st.session_state.selected_ticker)
    st.session_state.weekly_prices = weekly_prices(st.session_state.selected_ticker)

    st.session_state.balance_sheet, bs_reported_currency = get_balance_sheet(st.session_state.selected_ticker)
    st.session_state.income_statement, is_reported_currency = get_income_statement(st.session_state.selected_ticker)
    st.session_state.cash_flow, cf_reported_currency = get_cash_flow(st.session_state.selected_ticker)


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
        bs_col1, bs_col2 = st.columns(2)
        bs_col1.metric(label='Currency', value=bs_reported_currency)
        bs_col2.metric(label='Scale', value='Millions')
        st.checkbox(label='View Balance Sheet', key='show_bs', value=True)
        if st.session_state.show_bs:
            st.dataframe(df.style.pipe(make_pretty), use_container_width=True)


        st.session_state.selected_bs_line = st.multiselect(
            'Balance Sheet Line Item',
            options=st.session_state.balance_sheet.index,
            default=['totalAssets', 'totalLiabilities', 'totalShareholderEquity']
        )
        chart_df = st.session_state.balance_sheet.transpose()

        st.line_chart(data = chart_df,
                      y = st.session_state.selected_bs_line,
                      )


    with income_tab:
        df = st.session_state.income_statement
        is_col1, is_col2 = st.columns(2)
        is_col1.metric(label='Currency', value=is_reported_currency)
        is_col2.metric(label='Scale', value='Millions')
        st.checkbox(label='View Income Statement', key='show_is', value=True)
        if st.session_state.show_is:
            st.dataframe(df.style.pipe(make_pretty), use_container_width=True)

        st.session_state.selected_is_line = st.multiselect(
            'Income Statement Line Item',
            options=st.session_state.income_statement.index,
            default=['grossProfit', 'totalRevenue', 'costOfRevenue']
        )
        chart_df = st.session_state.income_statement.transpose()

        st.line_chart(data=chart_df,
                      y=st.session_state.selected_is_line,
                      )

    with cashflow_tab:
        df = st.session_state.cash_flow
        cf_col1, cf_col2 = st.columns(2)
        cf_col1.metric(label='Currency', value=cf_reported_currency)
        cf_col2.metric(label='Scale', value='Millions')
        st.checkbox(label='View Statement of Cash Flow', key='show_cf', value=True)
        if st.session_state.show_cf:
            st.dataframe(df.style.pipe(make_pretty), use_container_width=True)

        st.session_state.selected_cf_line = st.multiselect(
            'Cash Flow Line Item',
            options=st.session_state.cash_flow.index,
            default='changeInCashAndCashEquivalents'
        )
        chart_df = st.session_state.cash_flow.transpose()

        st.line_chart(data=chart_df, y=st.session_state.selected_cf_line)

    with news_tab:
        news = get_news(st.session_state.selected_ticker)
        st.subheader('I can summarize news for you!')
        col1, col2 = st.columns([1,7])
        col1.image('Resources/bot.jpeg')
        selected_news = col2.selectbox('Select News title and I will create you a summary of that article',
                                     options=[title['title'] for title in news],
                                     )
        st.session_state.selected_news = [url['link'] for url in news if url['title'] == selected_news][0]
        col2.button(label='**summarize!**', key='summarize_btn')

        if st.session_state.summarize_btn:
            st.session_state.news_summary = get_news_summary(text=st.session_state.selected_news,
                                                             ticker=st.session_state.selected_ticker)
            st.session_state.expanded = True

        if 'news_summary' not in st.session_state:
            st.session_state.expanded = False
            st.session_state.news_summary = ''

        with col2.expander(label='summary', expanded=st.session_state.expanded):
            st.write(st.session_state.news_summary)
