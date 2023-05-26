import streamlit as st
from typing import Callable


# define a function 'company_income_statement' which accepts two arguments:
# a Callable 'formatter' (likely a function to format data), and a string 'currency'
# (the currency in which the company's financials are reported)
def company_income_statement(formatter: Callable, currency: str):
    # load income statement data into a DataFrame
    df = st.session_state.income_statement

    # create two columns layout inside the 'Income Statement' tab
    is_col1, is_col2 = st.columns(2)

    # in the first column, display a metric for reported currency
    is_col1.metric(label='Currency', value=currency)

    # in the second column, display a metric for the scale (millions)
    is_col2.metric(label='Scale', value='Millions')

    # add a checkbox to control the visibility of the income statement DataFrame
    st.checkbox(label='View Income Statement', key='show_is', value=True)

    # if the 'View Income Statement' checkbox is checked, display the styled DataFrame
    if st.session_state.show_is:
        st.dataframe(df.style.pipe(formatter), use_container_width=True)

    # allow the user to select multiple line items from the income statement
    st.session_state.selected_is_line = st.multiselect(
        'Income Statement Line Item',
        options=st.session_state.income_statement.index,
        default=['grossProfit', 'totalRevenue', 'costOfRevenue']
    )

    # transpose the income statement DataFrame for the chart
    chart_df = st.session_state.income_statement.transpose()

    # create a line chart of the selected income statement line items over time
    st.line_chart(data=chart_df,
                  y=st.session_state.selected_is_line,
                  )
