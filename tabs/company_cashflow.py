import streamlit as st
from typing import Callable

def company_cash_flow(formatter: Callable, currency: str):
    # load cash flow data into a DataFrame
    df = st.session_state.cash_flow

    # create two columns layout inside the 'Statement of Cash Flow' tab
    cf_col1, cf_col2 = st.columns(2)

    # in the first column, display a metric for reported currency
    cf_col1.metric(label='Currency', value=currency)

    # in the second column, display a metric for the scale (millions)
    cf_col2.metric(label='Scale', value='Millions')

    # add a checkbox to control the visibility of the cash flow statement DataFrame
    st.checkbox(label='View Statement of Cash Flow', key='show_cf', value=True)

    # if the 'View Statement of Cash Flow' checkbox is checked, display the styled DataFrame
    if st.session_state.show_cf:
        st.dataframe(df.style.pipe(formatter), use_container_width=True)

    # allow the user to select a line item from the cash flow statement
    st.session_state.selected_cf_line = st.multiselect(
        'Cash Flow Line Item',
        options=st.session_state.cash_flow.index,
        default='changeInCashAndCashEquivalents'
    )

    # transpose the cash flow statement DataFrame for the chart
    chart_df = st.session_state.cash_flow.transpose()

    # create a line chart of the selected cash flow line item over time
    st.line_chart(data=chart_df, y=st.session_state.selected_cf_line)