"""
This code is part of the Computer Science Project of group 11.05:
Philippe Verdeja, Yannick Hafner, Remi de la Fortelle, Mara Ciglia and Sam Pellaud.
It contains the "News" page, split into a top movers section, a financial news feed and a markets overview.
The idea is to give the user a daily snapshot of what's moving the global markets at a glance.
On top of that, the page shows live indices from 5 regions and lets the user switch between 1 week, 1 month and 1 year views.
"""

import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.express as px

# Page configuration, title, subtitle and tab icon (logo without text)
# Logo and tab icon by Claude
st.set_page_config(
    page_title="Morning Market Digest",
    page_icon="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzNjAgMzYwIj48cmVjdCB3aWR0aD0iMzYwIiBoZWlnaHQ9IjM2MCIgcng9IjUwIiBmaWxsPSIjMGQxYjJhIi8+PHJlY3QgeD0iNjAiIHk9IjE4MCIgd2lkdGg9IjU1IiBoZWlnaHQ9IjE1MCIgcng9IjQiIGZpbGw9IiNmZmZmZmYiLz48cmVjdCB4PSIxNTIiIHk9IjIzMCIgd2lkdGg9IjU1IiBoZWlnaHQ9IjEwMCIgcng9IjQiIGZpbGw9IiNmZmZmZmYiLz48cmVjdCB4PSIyNDQiIHk9IjEyMCIgd2lkdGg9IjU1IiBoZWlnaHQ9IjIxMCIgcng9IjQiIGZpbGw9IiNmZmZmZmYiLz48cG9seWxpbmUgcG9pbnRzPSIzNSwyNjAgODcuNSwxODAgMTc5LjUsMjMwIDI4NSwxMDgiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzFmOGZmZiIgc3Ryb2tlLXdpZHRoPSIxNCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMjg1LDEwOCkgcm90YXRlKC00MS42MykiPjxwb2x5Z29uIHBvaW50cz0iLTI2LC0yMiAyMiwwIC0yNiwyMiIgZmlsbD0iIzFmOGZmZiIgc3Ryb2tlPSIjMWY4ZmZmIiBzdHJva2Utd2lkdGg9IjYiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L2c+PC9zdmc+",
    layout="wide"
)
st.title("**Morning Market Digest**")
# Date automatically updates every time the page loads
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")

st.page_link("Home.py", label="Go to Homepage")

# Adds the logo of our website at the top right corner
st.markdown("""
    <style>
    .easy-investing-logo {
        position: fixed;
        top: 60px;
        right: 20px;
        width: 130px;
        z-index: 9999;
    }
    </style>
    <div class="easy-investing-logo">
        <svg viewBox="0 0 680 500" xmlns="http://www.w3.org/2000/svg">
            <rect x="160" y="40" width="360" height="360" rx="50" fill="#0d1b2a"/>
            <rect x="220" y="220" width="55" height="150" rx="4" fill="#ffffff"/>
            <rect x="312" y="270" width="55" height="100" rx="4" fill="#ffffff"/>
            <rect x="404" y="160" width="55" height="210" rx="4" fill="#ffffff"/>
            <polyline points="195,300 247.5,220 339.5,270 445,148"
                      fill="none" stroke="#1f8fff" stroke-width="14"
                      stroke-linecap="round" stroke-linejoin="round"/>
            <g transform="translate(445,148) rotate(-41.63)">
                <polygon points="-26,-22 22,0 -26,22" fill="#1f8fff"
                         stroke="#1f8fff" stroke-width="6" stroke-linejoin="round"/>
            </g>
            <text x="340" y="465" font-size="58" font-weight="800"
                  text-anchor="middle" letter-spacing="-1"
                  font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">
                <tspan fill="#1f8fff">Easy</tspan><tspan fill="#ffffff"> Investing</tspan>
            </text>
        </svg>
    </div>
""", unsafe_allow_html=True)


@st.cache_data(ttl=1800) #longer cache time works, since news aren't updated super frequently
def get_headlines():
    import requests
    from bs4 import BeautifulSoup #to get the image of the news article
    feed = feedparser.parse("https://www.cnbc.com/id/100727362/device/rss/rss.html") #cnbc website to get the top geopolitical news articles, we can also add more websites if needed
    entries = []
    for entry in feed.entries[:6]: #how the news are displayed, and how many articles need to be shown
        title = entry.title
        link = entry.link #puts the link to the actual article
        image = None
        try:
            response = requests.get(link, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image = og_image["content"]
        except:
            pass  #if fetching fails for any article, just shows no image
        entries.append((title, link, image))
    return entries


def get_index_change(ticker):
    hist=yf.Ticker(ticker).history(period="5d")  #looks at the last 5 days so that even if the market is closed over the weekend or holiday it works
    if len(hist) < 2:
        return None, None
    prev=hist["Close"].iloc[-2] #looks at yesterday's closing price
    last=hist["Close"].iloc[-1] #looks at today's closing price, so today's most recent price if the markets haven't closed yet
    change=((last-prev)/prev)*100
    return round(last, 2), round(change, 2)  #so that the numbers show up with rounded decimals

@st.cache_data(ttl=300) #same logic as above for the cache, but since market data is updated more frequently, less time is put in the cache
def get_index_history(period): #this function is to create a graph of the different indices
    tickers=["^GSPC", "^STOXX", "^HSI", "^N225", "^KS200"]
    names={"^GSPC": "S&P 500", "^STOXX": "EuroStoxx 600", "^HSI": "Hang Seng", "^N225": "Nikkei 225", "^KS200": "Kospi 200"}
    data=yf.download(tickers, period=period, group_by="ticker")
    frames=[]
    for ticker in tickers:
        df=data[ticker][["Close"]].dropna().copy() #looking at each ticker individually, only looking at the "Close" column over the specified amount of time, while creating a copy to make sure the original isn't edited
        df["Index"]=names[ticker]
        df["Close"]=df["Close"]/df["Close"].iloc[0]*100  #normalise to 100 at the start so all lines begin at the same point
        frames.append(df)
    return pd.concat(frames).reset_index() #stacks all the individual ticker tables into one table


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
    return pd.DataFrame(gainers), pd.DataFrame(losers) #converts the data into a table

def fmt_price(x): #formats the stock/index price nicely by allowing the price to display "N/A" if yfinance doesn't find it instead of crashing
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:.2f}"


def fmt_change(x): #formatting the percentage change with colour and make sure that green is tied with positive, otherwise display red
    if x is None or pd.isna(x): #just in case there is an issue so that the website doesn't crash
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

with st.sidebar: #make sure the sidebar is present
    st.empty()

st.text(" ") #adding space between the title and the three columns below it, this was the easiest way I found to do it
st.text(" ")
st.text(" ")
st.text(" ")

#three column layout for the top gainers, news and top losers
left_col, news_col, right_col = st.columns([1, 2, 1]) #the 1, 2, 1 ratio makes the news column twice as wide as each movers column since it needs space for the pictures


#left column with top gainers
with left_col:
    st.markdown("<h3 style='color: green;'> Top Gainers</h3>", unsafe_allow_html=True) #HTML text editing to make the title green and allow this HTML since Streamlit seems to block it if I don't add the unsafe_allow_html=true
    st.caption("Live from Yahoo Finance")
    for _, row in top_gainers.iterrows(): #calling on the top_gainers table that was made above, since we don't need a row number, the _ is used as a placeholder
        st.markdown(               #company name in large bold text, ticker+change below it
            f"<p style='font-size:17px; font-weight:bold; margin-bottom:2px;'>{row['Name']}</p>"
            f"<p style='margin-top:0px; color:gray;'>{row['Ticker']} &nbsp;|&nbsp; "
            f"<span style='color:green;'>+{row['Change (%)']:.2f}%</span>",
            unsafe_allow_html=True,
        )
        st.divider()


#middle column with top news
with news_col:
    st.subheader("Top News") 
    inner_cols=st.columns(3) #display news in a 3-column grid inside the middle column
    for i, (title, link, image) in enumerate(headlines):
        with inner_cols[i%3]:  #i%3 cycles through columns 0, 1, 2 then back to 0
            if image:
                st.image(image, use_container_width=True)
            else: # Grey placeholder box if no image is available
                st.markdown(
                    "<div style='background:#e0e0e0; height:100px; border-radius:6px; "
                    "display:flex; align-items:center; justify-content:center; "
                    "color:#888; font-size:12px;'>No image</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(f"**[{title}]({link})**") #make it bold
            st.markdown("---")


#right column with top losers
with right_col:
    st.markdown("<h3 style='color: red;'> Top Losers</h3>", unsafe_allow_html=True) #HTML text editing to make the title red and allow this HTML since Streamlit seems to block it if I don't add the unsafe_allow_html=true
    st.caption("Live from Yahoo Finance")
    for _, row in top_losers.iterrows(): #calling on the top_losers table that was made above, since we don't need a row number, the _ is used as a placeholder
        #company name in large bold text, ticker+change below it
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
st.markdown("<h2 style='text-align: center;'>Markets</h3>", unsafe_allow_html=True) #centralising the "Markets" title to make it look nice, HTML was the easiest way to do that

period=st.radio("Time range", ["1W", "1M", "1Y"], horizontal=True, label_visibility="collapsed") #defining the time periods for the table
history=get_index_history(period)
chart_data=history.pivot(index="Date", columns="Index", values="Close") #pivot so each index becomes its own column
fig=px.line(history, x="Date", y="Close", color="Index")
st.plotly_chart(fig, use_container_width=True) #create chart

flag_urls = {                   #I tried to put in flag emojis but it never worked, so this was the way Claude told me to do it
    "col1": "https://flagcdn.com/32x24/us.png",
    "col2": "https://flagcdn.com/32x24/eu.png",
    "col3": "https://flagcdn.com/32x24/hk.png",
    "col4": "https://flagcdn.com/32x24/jp.png",
    "col5": "https://flagcdn.com/32x24/kr.png"}
col1, col2, col3, col4, col5=st.columns(5)  #five different columns, one for each ticker, with the flag, title, price and change in each column
with col1:
    st.image(flag_urls["col1"], width=32); st.metric("S&P 500", sp500_price, f"{sp500_change}%")
with col2:
    st.image(flag_urls["col2"], width=32); st.metric("EuroStoxx 600", eurostoxx600_price, f"{eurostoxx600_change}%")
with col3:
    st.image(flag_urls["col3"], width=32); st.metric("HangSeng Index", HangSeng_price, f"{HangSeng_change}%")
with col4:
    st.image(flag_urls["col4"], width=32); st.metric("Nikkei 225", Nikkei225_price, f"{Nikkei225_change}%")
with col5:
    st.image(flag_urls["col5"], width=32); st.metric("Kospi 200", Kospi200_price, f"{Kospi200_change}%")

with st.expander("💡 What does this mean?"): #beginner-friendly part to quickly explain how to read infos
    st.write("""
    - In the graph, all indices start at 100 regardless of their actual value to better show the difference in performance
    - Price = current level of the index in its own currency  
    - % change = how much it moved since yesterday  
    - 🟢 = market went up  
    - 🔴 = market went down  
    """)
