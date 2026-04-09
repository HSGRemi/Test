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

def format_metric(price, change):
    if price == "N/A" or change == "N/A":
        return "N/A", "N/A"
    return f"{price:.2f}", f"{change:.2f}%"

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
    st.markdown(f"**S&P 500**  \nPrice: {sp500_price:.2f}  \nChange: {sp500_change:+.2f}%")

with col2:
    st.markdown(f"**Eurostoxx 600**  \nPrice: {eurostoxx600_price:.2f}  \nChange: {eurostoxx600_change:+.2f}%")

with col3:
    st.markdown(f"**MSCI World**  \nPrice: {MSCIworld_price:.2f}  \nChange: {MSCI_change:+.2f}%")

with col4:
    st.markdown(f"**HangSeng Index**  \nPrice: {HangSeng_price:.2f}  \nChange: {HangSeng_change:+.2f}%")

with col5:
    st.markdown(f"**Nikkei 225**  \nPrice: {Nikkei225_price:.2f}  \nChange: {Nikkei225_change:+.2f}%")

with col6:
    st.markdown(f"**KOSPI 200**  \nPrice: {Kospi200_price:.2f}  \nChange: {Kospi200_change:+.2f}%")

