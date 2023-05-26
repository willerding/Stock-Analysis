import requests
import openai
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup
import yaml

# load secrets
secrets = yaml.safe_load(open('secrets.yaml'))

openai.api_key = secrets['openai']


# use Streamlit's cache decorator to store the result of this function, so it only runs once
# this function takes a ticker symbol as a string, fetches the corresponding financial symbol with yfinance and returns the news related to this symbol
@st.cache_data
def get_news(ticker: str):
    symbol = yf.Ticker(ticker= ticker)
    return symbol.get_news()


# use Streamlit's cache decorator to store the result of this function, so it only runs once
# this function takes a URL as a string, makes a GET request to fetch the web page, parses the content with BeautifulSoup, and returns the text of the news article
@st.cache_data
def get_news_text(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='lxml')
    text = soup.find('div', attrs={'class': 'caas-body'}).text
    return text


# use Streamlit's cache decorator to store the result of this function, so it only runs once
# this function takes a text string (a news article) and a ticker string, sends them to the OpenAI GPT-3.5-turbo model to generate a summary, and returns the summary text
@st.cache_data
def get_news_summary(text: str, ticker: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello!"},
            {"role": "user", "content": "Please summarize the news article briefly. Also highlight the parts "
                                        f"that talk about {ticker}"
             },
            {"role": "user", "content": f"{text}"}
        ]
    )
    return response['choices'][0]['message']['content']


def company_news(ticker: str):
    news = get_news(ticker)
    st.subheader('I can summarize news for you!')
    col1, col2 = st.columns([1, 7])
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
