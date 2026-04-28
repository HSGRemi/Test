import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Morning Market Digest", layout="wide")
st.title("**Morning Market Digest**")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")  #date automatically updates every time the page loads

@st.cache_data(ttl=1800)
def get_headlines():
    import requests
    from bs4 import BeautifulSoup
    feed = feedparser.parse("https://www.cnbc.com/id/100727362/device/rss/rss.html")
    entries = []
    for entry in feed.entries[:6]:
        title = entry.title
        link = entry.link
        image = None
        try:
            response = requests.get(link, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image = og_image["content"]
        except:
            pass  #if fetching fails for any article, just show no image
        entries.append((title, link, image))
    return entries


def get_index_change(ticker):
    hist=yf.Ticker(ticker).history(period="5d")  #looks at the last 5 days so that even if the market is closed over the weekend or holiday it works
    if len(hist) < 2:
        return None, None
    prev=hist["Close"].iloc[-2]
    last=hist["Close"].iloc[-1]
    change=((last-prev)/prev)*100
    return round(last, 2), round(change, 2)  #so that the numbers show up with rounded decimals

@st.cache_data(ttl=300) #same logic as above, this function is to create a graph of the different indices
def get_index_history(period):
    tickers=["^GSPC", "^STOXX", "^HSI", "^N225", "^KS200"]
    names={"^GSPC": "S&P 500", "^STOXX": "EuroStoxx 600", "^HSI": "Hang Seng", "^N225": "Nikkei 225", "^KS200": "Kospi 200"}
    data=yf.download(tickers, period=period, group_by="ticker")
    frames=[]
    for ticker in tickers:
        df=data[ticker][["Close"]].dropna().copy()
        df["Index"]=names[ticker]
        df["Close"]=df["Close"]/df["Close"].iloc[0]*100  #normalise to 100 at the start so all lines begin at the same point
        frames.append(df)
    return pd.concat(frames).reset_index()


@st.cache_data(ttl=300)  #main reason I used caches, since yfinance regularly crashes if one user calls upon it too much
def get_all_indices():
    tickers=["^GSPC", "^STOXX", "^HSI", "^N225", "^KS200"]  #selection of biggest tickers
    data=yf.download(tickers, period="5d", group_by="ticker")
    results={}
    for ticker in tickers:
        try:
            df=data[ticker].dropna()  #dropna drops missing values from the downloaded tickers
            if len(df) < 2:
                results[ticker] = (None, None)
                continue
            prev=df["Close"].iloc[-2]
            last=df["Close"].iloc[-1]
            change=((last-prev)/prev)*100
            results[ticker]=(round(last, 2), round(change, 2))
        except:
            results[ticker]=(None, None)
    return results

@st.cache_data(ttl=300)  #same cache logic as above
def get_movers():
    gainers_data=yf.screen("day_gainers")  #pulls Yahoo Finance's own top gainers list
    gainers=[
        {"Ticker": q["symbol"], "Name": q.get("shortName", q["symbol"]), "Price": round(q.get("regularMarketPrice", 0), 2), "Change (%)": round(q.get("regularMarketChangePercent", 0), 2)}
        for q in gainers_data.get("quotes", [])[:5]  #take only the top 5
    ]

    losers_data=yf.screen("day_losers")  #pulls Yahoo Finance's own top losers list
    losers=[
        {"Ticker": q["symbol"], "Name": q.get("shortName", q["symbol"]), "Price": round(q.get("regularMarketPrice", 0), 2), "Change (%)": round(q.get("regularMarketChangePercent", 0), 2)}
        for q in losers_data.get("quotes", [])[:5]  #take only the top 5
    ]
    return pd.DataFrame(gainers), pd.DataFrame(losers)

def fmt_price(x):
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:.2f}"


def fmt_change(x):
    if x is None or pd.isna(x):
        return "N/A"
    color="🟢" if x > 0 else "🔴"
    return f"{color} {x:.2f}%"


#fetching all the data
headlines=get_headlines()
results=get_all_indices()
top_gainers, top_losers=get_movers()

#defining the index names for the yfinance API
sp500_price, sp500_change=results["^GSPC"]
eurostoxx600_price, eurostoxx600_change=results["^STOXX"]
HangSeng_price, HangSeng_change=results["^HSI"]
Nikkei225_price, Nikkei225_change=results["^N225"]
Kospi200_price, Kospi200_change=results["^KS200"]

with st.sidebar:
    st.empty()

st.text(" ") #adding space between the title and the three columns below it
st.text(" ")
st.text(" ")
st.text(" ")

#creating a three column layout for the top gainers, news and top losers
left_col, news_col, right_col = st.columns([1, 2, 1]) #the 1, 2, 1 ratio makes the news column twice as wide as each movers column since it needs space for the pictures


#left column with top gainers
with left_col:
    st.markdown("<h3 style='color: green;'> Top Gainers</h3>", unsafe_allow_html=True)
    st.caption("Live from Yahoo Finance")
    for _, row in top_gainers.iterrows():
        # Company name in large bold text, ticker + change below it
        st.markdown(
            f"<p style='font-size:17px; font-weight:bold; margin-bottom:2px;'>{row['Name']}</p>"
            f"<p style='margin-top:0px; color:gray;'>{row['Ticker']} &nbsp;|&nbsp; "
            f"<span style='color:green;'>+{row['Change (%)']:.2f}%</span>",
            unsafe_allow_html=True,
        )
        st.divider()


#middle column with top news
with news_col:
    st.subheader("Top News") # Display news in a 3-column grid inside the middle column
    inner_cols = st.columns(3)
    for i, (title, link, image) in enumerate(headlines):
        with inner_cols[i % 3]:  #i % 3 cycles through columns 0, 1, 2 then back to 0
            if image:
                st.image(image, use_container_width=True)
            else: # Grey placeholder box if no image is available
                st.markdown(
                    "<div style='background:#e0e0e0; height:100px; border-radius:6px; "
                    "display:flex; align-items:center; justify-content:center; "
                    "color:#888; font-size:12px;'>No image</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(f"**[{title}]({link})**")
            st.markdown("---")


#right column with top losers
with right_col:
    st.markdown("<h3 style='color: red;'> Top Losers</h3>", unsafe_allow_html=True)
    st.caption("Live from Yahoo Finance")
    for _, row in top_losers.iterrows():
        #company name in large bold text, ticker + change below it
        st.markdown(
            f"<p style='font-size:17px; font-weight:bold; margin-bottom:2px;'>{row['Name']}</p>"
            f"<p style='margin-top:0px; color:gray;'>{row['Ticker']} &nbsp;|&nbsp; "
            f"<span style='color:red;'>{row['Change (%)']:.2f}%</span>",
            unsafe_allow_html=True,
        )
        st.divider()

st.text(" ") #adding space between the three columns and the Markets part, otherwise looks quite confusing
st.text(" ")
st.divider()

#index part
st.markdown("<h2 style='text-align: center;'>Markets</h3>", unsafe_allow_html=True)

period=st.radio("Time range", ["1wk", "1mo", "1y"], horizontal=True, label_visibility="collapsed")
history=get_index_history(period)
chart_data=history.pivot(index="Date", columns="Index", values="Close") #pivot so each index becomes its own column
fig=px.line(history, x="Date", y="Close", color="Index")
st.plotly_chart(fig, use_container_width=True)

col1, col2, col3, col4, col5 = st.columns(5)  #five different columns, one for each ticker
with col1:
    st.metric("S&P 500", sp500_price, f"{sp500_change}%")
with col2:
    st.metric("EuroStoxx 600", eurostoxx600_price, f"{eurostoxx600_change}%")
with col3:
    st.metric("HangSeng Index", HangSeng_price, f"{HangSeng_change}%")
with col4:
    st.metric("Nikkei 225", Nikkei225_price, f"{Nikkei225_change}%")
with col5:
    st.metric("Kospi 200", Kospi200_price, f"{Kospi200_change}%")
