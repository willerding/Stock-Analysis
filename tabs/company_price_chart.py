import streamlit as st
from alpha_vantage.timeseries import TimeSeries
import yaml

# load secrets
secrets = yaml.safe_load(open('secrets.yaml'))


def company_price_chart():
    ts = TimeSeries(key=secrets['alpha_vantage'], output_format='pandas')

    @st.cache_data
    def weekly_prices(ticker: str):
        data = ts.get_weekly_adjusted(ticker)[0]
        data.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low',
                             '4. close': 'close', '5. adjusted close': 'adjusted close',
                             '6. volume': 'volume', '7. dividend amount': 'dividend amount',
                             '8. split coefficient': 'split coefficient'},
                    inplace=True)
        return data

    # fetch and store the weekly prices for the selected ticker
    st.session_state.weekly_prices = weekly_prices(st.session_state.selected_ticker)

    st.line_chart(st.session_state.weekly_prices, y='adjusted close')
