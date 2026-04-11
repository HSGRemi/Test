import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime
import flag

# PAGE SETTINGS
st.set_page_config(page_title="Morning Market Digest", layout="centered")

# Simple background color (easy to understand)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f6ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Morning Market Digest")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")

st.sidebar.title("Morning Market Digest")
st.sidebar.write("Simple overview of markets and news.")

# GET NEWS
@st.cache_data(ttl=1800)
def get_headlines():
    feeds = ["https://www.cnbc.com/id/100727362/device/rss/rss.html"]
    feed = feedparser.parse(feeds[0])
    return [(entry.title, entry.link) for entry in feed.entries[:6]]

# GET MARKET DATA
@st.cache_data(ttl=300)
def get_all_indices():
    tickers = ["^GSPC", "^STOXX", "^HSI", "^N225", "^KS200"]
    data = yf.download(tickers, period="5d", group_by="ticker")

    results = {}

    for ticker in tickers:
        try:
            df = data[ticker].dropna()

            if len(df) < 2:
                results[ticker] = (None, None)
                continue

            prev = df["Close"].iloc[-2]
            last = df["Close"].iloc[-1]
            change = ((last - prev) / prev) * 100

            results[ticker] = (round(last, 2), round(change, 2))
        except:
            results[ticker] = (None, None)

    return results

# FORMAT FUNCTIONS
def format_price(x):
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:.2f}"

def format_change(x):
    if x is None or pd.isna(x):
        return "N/A"

# LOAD DATA
headlines = get_headlines()
results = get_all_indices()

# NEWS SECTION
st.subheader("Top News")

for title, link in headlines:
    st.markdown(f"- [{title}]({link})")

# MARKETS SECTION WITH FLAGS
st.subheader("Global Markets")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    price, change = results["^GSPC"]
    st.metric("S&P 500 🇺🇸", format_price(price), format_change(change))

with col2:
    price, change = results["^STOXX"]
    st.metric("EuroStoxx 600 🇪🇺", format_price(price), format_change(change))

with col3:
    price, change = results["^HSI"]
    st.metric("Hang Seng 🇭🇰", format_price(price), format_change(change))

with col4:
    price, change = results["^N225"]
    st.metric("Nikkei 225 🇯🇵", format_price(price), format_change(change))

with col5:
    price, change = results["^KS200"]
    st.metric("KOSPI 200 🇰🇷", format_price(price), format_change(change))

flag.flag("GBENG")'🏴󠁧󠁢󠁥󠁮󠁧'
flag.dflagize("Flag of the USA 🇺🇸")

# BEGINNER HELP BOX
with st.expander("💡 What does this mean?"):
    st.write("""
    - Price = current level of the index  
    - % change = how much it moved since yesterday  
    - 🟢 = market went up  
    - 🔴 = market went down  
    """)
