import streamlit as st

def company_info(company_detail: dict):
    # display a Streamlit metric widget with the company name as the label and the ticker symbol as the value
    st.metric(label=company_detail['Name'],
              value=company_detail['Symbol'])

    # render the company description as markdown
    st.markdown(company_detail['Description'])

    # write the company's asset type to the tab
    st.write(company_detail['AssetType'])