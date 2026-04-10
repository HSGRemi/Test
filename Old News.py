import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime

st.sidebar.title("Morning Market Digest")

st.set_page_config(page_title="Morning Market Digest", layout="centered")

st.title("Morning Market Digest")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")

@st.cache_data(ttl=1800)
def get_headlines():
    url="http://rss.cnn.com/rss/edition_world.rss"
    feed=feedparser.parse(url)
    return [(entry.title, entry.link) for entry in feed.entries[:5]]

def get_index_change(ticker):
    hist=yf.Ticker(ticker).history(period="5d")
    if len(hist)<2:
        return None, None
    prev=hist["Close"].iloc[-2]
    last=hist["Close"].iloc[-1]
    change=((last - prev) / prev) * 100
    return round(last, 2), round(change, 2)

@st.cache_data(ttl=300)
def get_all_indices():
    tickers=["^GSPC", "^STOXX", "^URTH", "^HSI", "^N225", "^KS200"]
    data = yf.download(tickers, period="5d", group="ticker")
    results={}
    for ticker in tickers:
        try:
            hist=data[ticker]
            prev=hist["Close"].iloc[-2]
            last=hist["Close"].iloc[-1]
            change=((last - prev) / prev) * 100
            
            results[ticker] = (round(last, 2), round(change, 2))
        except:
            results[ticker] = (None, None)
    return results

headlines=get_headlines()

results = get_all_indices()

sp500_price, sp500_change=results["^GSPC"]
eurostoxx600_price, eurostoxx600_change=results["^STOXX"]
MSCIworld_price, MSCI_change=results["^URTH"]
HangSeng_price, HangSeng_change=results["^HSI"]
Nikkei225_price, Nikkei225_change=results["^N225"]
Kospi200_price, Kospi200_change=results["^KS200"]

st.subheader("Top News")

for title, link in headlines:
    st.markdown(f"- [{title}]({link})")

st.subheader("Markets")

col1, col2=st.columns(2)

with col1:
    st.metric("S&P 500", sp500_price, f"{sp500_change}%")

with col2:
    st.metric("EuroStoxx 600", eurostoxx600_price, f"{eurostoxx600_change}%")

with col3:
    st.metric("MSCI World", MSCIworld_price, f"{MSCI_change}%")

with col4:
    st.metric("HangSeng Index", HangSeng_price, f"{HangSeng_change}%")

with col5:
    st.metric("Nikkei 225", Nikkei225_price, f"{Nikkei225_change}%")

with col6:
    st.metric("Kospi 200", Kospi200_price, f"{Kospi200_change}%")
