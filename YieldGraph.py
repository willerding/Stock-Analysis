"""
Author Hamid, Vakilzadeh PhD
November 2022

"""
import datetime
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd


# get stock prices
def get_market_data(selected_ticker, start=None, end=None):
    # Ticker
    ticker = yf.Ticker(selected_ticker)
    # get data
    prices = ticker.history(period='max', interval='1mo')

    # get dividends from the initial prices file
    dividends = prices[prices['Dividends'] != 0]

    # remove dividends from the prices file
    prices.dropna(subset=['Open'], inplace=True)
    prices.drop(columns=['Dividends'], inplace=True)
    prices.reset_index(inplace=True, drop=False)

    # add year column to price data
    prices['year'] = pd.DatetimeIndex(prices['Date']).year
    # dividends of the company
    dividends.drop(columns=['Open', 'High', 'Low', 'Close',
                            'Volume', 'Stock Splits'], inplace=True)
    dividends.reset_index(inplace=True, drop=False)

    # calculate annual dividends
    if len(dividends) > 0:
        pays_dividend = True
        dividends['year'] = pd.DatetimeIndex(dividends['Date']).year
        annual_dividends = dividends.groupby('year')['Dividends'] \
            .sum().rename('annual_dividends').reset_index()

        last_year_dividends = dividends.groupby('year')['Dividends'] \
            .sum().shift(periods=1).rename('last_year_dividends').reset_index()

        prices = pd.merge(left=prices,
                          right=annual_dividends,
                          on='year',
                          how='left')
        prices = pd.merge(left=prices,
                          right=last_year_dividends,
                          on='year',
                          how='left')

    else:
        pays_dividend = False
        prices['annual_dividends'] = 0

    prices['Yield'] = prices['annual_dividends'] / prices['Close']

    return dict(prices=prices, pays_dividend=pays_dividend)


# calculate undervalue and overvalue prices
def yield_calculations(data, min_yield, max_yield):
    data['overvalue_price'] = data['last_year_dividends'] / min_yield
    data['undervalue_price'] = data['last_year_dividends'] / max_yield


# create graph
def graph(data):
    fig = go.Figure(data=go.Ohlc(x=data['Date'],
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Monthly Stock Price'))
    fig.update(layout_xaxis_rangeslider_visible=True)
    if 'undervalue_price' in data.columns:
        fig.add_traces([go.Line(x=data['Date'],
                                y=data['overvalue_price'],
                                name='Overvalue Price'),
                        go.Line(x=data['Date'],
                                y=data['undervalue_price'],
                                name='Undervalue Price')
                        ])

    st.plotly_chart(fig)


if __name__ == '__main__':
    # input ticker
    ticker = st.text_input(label='Enter Ticker', placeholder='AAPL', value='AAPL')

    # two columns
    col1, col2 = st.columns(2)
    # input start and end date
    with col1:
        start_date = st.date_input(label='Start Date',
                                   value=datetime.date(2015, 1, 1),
                                   min_value=datetime.date(1900, 1, 1),
                                   max_value=datetime.date.today())
    with col2:
        end_date = st.date_input(label='End Date',
                                 value=datetime.date.today(),
                                 min_value=datetime.date(1900, 1, 1),
                                 max_value=datetime.date.today())

    # get historical data
    market_data = get_market_data(selected_ticker=ticker,
                                  start=start_date,
                                  end=end_date)

    historical_prices = market_data['prices']
    dividends = market_data['pays_dividend']

    div_col1, div_col2 = st.columns(2)
    if dividends:
        with div_col1:
            # Desired minimum yield
            overvalue_yield = st.slider(label='Overvalue Yield',
                                        value=0.0,
                                        min_value=0.0, max_value=20.0,
                                        step=0.05,
                                        format='%f%%') / 100

        with div_col2:
            # Desired minimum yield
            undervalue_yield = st.slider(label='Undervalue Yield',
                                         value=0.0,
                                         min_value=0.0, max_value=20.0,
                                         step=0.05,
                                         format='%f%%') / 100

        # calculate yields
        yield_calculations(data=historical_prices, min_yield=overvalue_yield, max_yield=undervalue_yield)

    else:
        st.warning('This company does not pay dividends.')

    # show graph
    with st.container():
        graph(data=historical_prices)

    # show data
    st.dataframe(historical_prices)
