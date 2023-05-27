# Import the Streamlit library for building web apps
import streamlit as st
# Import the TimeSeries class from the alpha_vantage library for fetching stock data
from alpha_vantage.timeseries import TimeSeries
# Import the YAML library for parsing YAML files
import yaml


# Define a function for displaying a company's price chart
def company_price_chart():
    # Initialize a TimeSeries object with the API key from the secrets file
    ts = TimeSeries(key=st.secrets['alpha_vantage'], output_format='pandas')

    # Define a function for fetching weekly stock prices,
    # decorated with Streamlit's caching decorator to speed up subsequent calls
    @st.cache_data
    def weekly_prices(ticker: str):
        # Fetch the weekly adjusted stock data for the specified ticker
        data = ts.get_weekly_adjusted(ticker)[0]
        # Rename the columns to remove the numeric prefixes
        data.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low',
                             '4. close': 'close', '5. adjusted close': 'adjusted close',
                             '6. volume': 'volume', '7. dividend amount': 'dividend amount',
                             '8. split coefficient': 'split coefficient'},
                    inplace=True)
        return data

    # Fetch and store the weekly prices for the selected ticker in Streamlit's session state
    st.session_state.weekly_prices = weekly_prices(st.session_state.selected_ticker)

    # Display a line chart of the weekly prices, with the y-axis representing the adjusted close price
    st.line_chart(st.session_state.weekly_prices, y='adjusted close')
