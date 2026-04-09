import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime

st.sidebar.title("Morning Market Digest")

st.set_page_config(page_title="Morning Market Digest", layout="centered")

st.title("Morning Market Digest")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")

def get_headlines():
    url="https://feeds.bbci.co.uk/news/business/rss.xml"
    feed=feedparser.parse(url)
    return [entry.title for entry in feed.entries[:5]]

def get_index_change(ticker):
    hist=yf.Ticker(ticker).history(period="5d")
    hist = hist["Close"].dropna()
    if len(hist)<2:
        return "N/A", "N/A"
    prev, last = hist.iloc[-2], hist.iloc[-1]
    change = ((last - prev) / prev) * 100
    return round(last, 2), round(change, 2)

headlines=get_headlines()

sp500_price, sp500_change=get_index_change("^GSPC")
eurostoxx600_price, eurostoxx600_change=get_index_change("^STOXX")
MSCIworld_price, MSCI_change=get_index_change("^ACWI")
HangSeng_price, HangSeng_change=get_index_change("^HSI")
Nikkei225_price, Nikkei225_change=get_index_change("^N225")
Kospi200_price, Kospi200_change=get_index_change("^KS200")

st.subheader("Top News")

for h in headlines:
    st.markdown(f"- {h}")

st.subheader("Markets")

col1, col2, col3, col4, col5, col6=st.columns(6)

with col1:
    price, change=format_metric(sp500_price, sp500_change)
    st.metric("S&P 500", sp500_price, f"{sp500_change}%")

with col2:
    price, change=format_metric(eurostoxx600_price, eurostoxx600_change)
    st.metric("EuroStoxx 600", price, change)

with col3:
    price, change=format_metric(MSCIworld_price, MSCI_change)
    st.metric("MSCI World", MSCIworld_price, f"{MSCI_change}%")

with col4:
    price, change=format_metric(HangSeng_price, HangSeng_change)
    st.metric("HangSeng Index", HangSeng_price, f"{HangSeng_change}%")

with col5:
    price, change=format_metric(Nikkei225_price, Nikkei225_change)
    st.metric("Nikkei 225", Nikkei225_price, f"{Nikkei225_change}%")

with col6:
    price, change=format_metric(Kospi200_price, Kospi200_change)
    st.metric("Kospi 200", Kospi200_price, f"{Kospi200_change}%")
