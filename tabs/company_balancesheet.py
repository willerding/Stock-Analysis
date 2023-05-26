import streamlit as st
from typing import Callable


# define a function 'company_balance_sheet' which accepts two arguments:
# a Callable 'formatter' (likely a function to format data), and a string 'currency'
# (the currency in which the company's financials are reported)
def company_balance_sheet(formatter: Callable, currency: str):
    # load balance sheet data into a DataFrame
    df = st.session_state.balance_sheet

    # create two columns layout inside the 'Balance Sheet' tab
    bs_col1, bs_col2 = st.columns(2)

    # in the first column, display a metric for reported currency
    bs_col1.metric(label='Currency', value=currency)

    # in the second column, display a metric for the scale (millions)
    bs_col2.metric(label='Scale', value='Millions')

    # add a checkbox to control the visibility of the balance sheet DataFrame
    st.checkbox(label='View Balance Sheet', key='show_bs', value=True)

    # if the 'View Balance Sheet' checkbox is checked, display the styled DataFrame
    if st.session_state.show_bs:
        st.dataframe(df.style.pipe(formatter), use_container_width=True)

    # allow the user to select multiple line items from the balance sheet
    st.session_state.selected_bs_line = st.multiselect(
        'Balance Sheet Line Item',
        options=st.session_state.balance_sheet.index,
        default=['totalAssets', 'totalLiabilities', 'totalShareholderEquity']
    )

    # transpose the balance sheet DataFrame for the chart
    chart_df = st.session_state.balance_sheet.transpose()

    # create a line chart of the selected balance sheet line items over time
    st.line_chart(data=chart_df,
                  y=st.session_state.selected_bs_line,
                  )