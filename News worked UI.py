import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime
 
st.set_page_config(page_title="Morning Market Digest", layout="centered")
st.title("Morning Market Digest")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")  # date automatically updates every time the page loads
 
@st.cache_data(ttl=1800)  # cache so that there aren't constant requests to the external websites and thus no risk of being blocked due to too high usage
def get_headlines():
    feeds = ["https://www.cnbc.com/id/100727362/device/rss/rss.html"]  # possibility of using multiple websites, but this one works well enough
    entries = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:6]:  # takes the top 6 headlines
            title = entry.title
            link = entry.link
            # Try to grab the article image from the RSS feed metadata
            image = None
            if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                image = entry.media_thumbnail[0]["url"]
            elif hasattr(entry, "media_content") and entry.media_content:
                image = entry.media_content[0].get("url", None)
            entries.append((title, link, image))
    return entries
 
 
def get_index_change(ticker):
    hist = yf.Ticker(ticker).history(period="5d")  # looks at the last 5 days so that even if the market is closed over the weekend or holiday it works
    if len(hist) < 2:
        return None, None
    prev = hist["Close"].iloc[-2]
    last = hist["Close"].iloc[-1]
    change = ((last - prev) / prev) * 100
    return round(last, 2), round(change, 2)  # so that the numbers show up with rounded decimals
 
 
@st.cache_data(ttl=300)  # main reason I used caches, since yfinance regularly crashes if one user calls upon it too much
def get_all_indices():
    tickers = ["^GSPC", "^STOXX", "^HSI", "^N225", "^KS200"]  # selection of biggest tickers
    data = yf.download(tickers, period="5d", group_by="ticker")
    results = {}
    for ticker in tickers:
        try:
            df = data[ticker].dropna()  # dropna drops missing values from the downloaded tickers
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
 
 
@st.cache_data(ttl=300)  # same cache logic as above
def get_movers():# yfinance has a built-in screener that pulls Yahoo Finance's own top gainers/losers lists. This is the same data shown on finance.yahoo.com/markets/stocks/gainers
    screener = yf.Screener()
    screener.set_predefined_body("day_gainers") # Pull top gainers
    gainers_data = screener.response  # returns a dict with a "quotes" key containing stock info
    gainers = [
        {"Ticker": q["symbol"], "Name": q.get("shortName", q["symbol"]), "Price": round(q.get("regularMarketPrice", 0), 2), "Change (%)": round(q.get("regularMarketChangePercent", 0), 2)}
        for q in gainers_data.get("quotes", [])[:5]  # take only the top 5
    ]
    screener.set_predefined_body("day_losers")    # Pull top losers
    losers_data = screener.response
    losers = [
        {"Ticker": q["symbol"], "Name": q.get("shortName", q["symbol"]), "Price": round(q.get("regularMarketPrice", 0), 2), "Change (%)": round(q.get("regularMarketChangePercent", 0), 2)}
        for q in losers_data.get("quotes", [])[:5]  # take only the top 5
    ]
 
    return pd.DataFrame(gainers), pd.DataFrame(losers)
 
 
def fmt_price(x):
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:.2f}"
 
 
def fmt_change(x):
    if x is None or pd.isna(x):
        return "N/A"
    color = "🟢" if x > 0 else "🔴"
    return f"{color} {x:.2f}%"
 
#getting all the necessary info
headlines = get_headlines()
results = get_all_indices()
top_gainers, top_losers = get_movers()

#defining the index name for the yfinance API 
sp500_price, sp500_change = results["^GSPC"]
eurostoxx600_price, eurostoxx600_change = results["^STOXX"]
HangSeng_price, HangSeng_change = results["^HSI"]
Nikkei225_price, Nikkei225_change = results["^N225"]
Kospi200_price, Kospi200_change = results["^KS200"]
 
 
st.subheader("Top News") #news section
 
# Display news in a 3-column grid, two rows of 3 articles each with the article image if there's one
cols = st.columns(3)
for i, (title, link, image) in enumerate(headlines):
    with cols[i % 3]:  # i % 3 cycles through columns 0, 1, 2 then back to 0
        if image:
            st.image(image, use_container_width=True)
        else:
            # Grey placeholder box if no image is available
            st.markdown(
                "<div style='background:#e0e0e0; height:120px; border-radius:6px; "
                "display:flex; align-items:center; justify-content:center; "
                "color:#888; font-size:13px;'>No image</div>",
                unsafe_allow_html=True,
            )
        st.markdown(f"**[{title}]({link})**")  # bold clickable headline
        st.markdown("---")  # thin divider between articles in the same column
 
 
st.subheader("Top Movers & Losers") #top losers and gainers section
st.caption("Live data from Yahoo Finance's day gainers/losers screener")
 
gainer_col, loser_col = st.columns(2)
 
with gainer_col:
    st.markdown("### 🟢 Top Gainers")
    for _, row in top_gainers.iterrows():
        st.metric(
            label=f"{row['Ticker']} — {row['Name']}",
            value=f"${row['Price']:.2f}",
            delta=f"{row['Change (%)']:.2f}%"
        )
 
with loser_col:
    st.markdown("### 🔴 Top Losers")
    for _, row in top_losers.iterrows():
        st.metric(
            label=f"{row['Ticker']} — {row['Name']}",
            value=f"${row['Price']:.2f}",
            delta=f"{row['Change (%)']:.2f}%"
        )
 
st.subheader("Markets") #index section
col1, col2, col3, col4, col5 = st.columns(5)  # five different columns, one for each ticker
 
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
