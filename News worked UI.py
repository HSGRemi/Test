import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime

# ── PAGE SETTINGS ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Morning Market Digest", layout="centered")

# ── BOLD BACKGROUND BLOBS + GLOBAL STYLES ──────────────────────────────────────
st.markdown(
    """
    <style>
    /* Import a fun, friendly font */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

    /* Base background */
    .stApp {
        background-color: #f0f6ff;
        font-family: 'Nunito', sans-serif;
    }

    /* Hide default Streamlit header padding so blobs sit flush */
    .block-container {
        padding-top: 2rem;
        position: relative;
        z-index: 1;
    }

    /* ── THE BLOBS ── injected as fixed pseudo-elements on the body */
    body::before,
    body::after {
        content: '';
        position: fixed;
        z-index: 0;
        pointer-events: none;
        border-radius: 50%;
        filter: blur(0px);
    }

    /* We create 6 blobs using a single <div> injected below */
    .blob-container {
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
    }

    .blob {
        position: absolute;
        border-radius: 60% 40% 55% 45% / 50% 60% 40% 50%;
        opacity: 0.55;
    }

    /* Individual blob sizes, positions, colours */
    .blob-1 {
        width: 340px; height: 300px;
        background: #FF4ECD;          /* hot pink */
        top: -80px; left: -100px;
        border-radius: 72% 28% 60% 40% / 45% 55% 45% 55%;
        animation: wobble1 8s ease-in-out infinite alternate;
    }
    .blob-2 {
        width: 280px; height: 260px;
        background: #FFD93D;          /* sunshine yellow */
        top: 30px; right: -90px;
        border-radius: 40% 60% 35% 65% / 60% 40% 60% 40%;
        animation: wobble2 10s ease-in-out infinite alternate;
    }
    .blob-3 {
        width: 380px; height: 320px;
        background: #6CF0C2;          /* mint green */
        top: 38%; left: -140px;
        border-radius: 55% 45% 70% 30% / 40% 60% 40% 60%;
        animation: wobble3 12s ease-in-out infinite alternate;
    }
    .blob-4 {
        width: 300px; height: 280px;
        background: #4FC3F7;          /* sky blue */
        top: 45%; right: -110px;
        border-radius: 30% 70% 45% 55% / 65% 35% 65% 35%;
        animation: wobble1 9s ease-in-out infinite alternate-reverse;
    }
    .blob-5 {
        width: 260px; height: 240px;
        background: #FF7043;          /* coral orange */
        bottom: 80px; left: 10%;
        border-radius: 65% 35% 50% 50% / 35% 65% 35% 65%;
        animation: wobble2 11s ease-in-out infinite alternate;
    }
    .blob-6 {
        width: 220px; height: 200px;
        background: #B388FF;          /* lavender purple */
        bottom: 40px; right: 8%;
        border-radius: 40% 60% 60% 40% / 50% 50% 50% 50%;
        animation: wobble3 7s ease-in-out infinite alternate-reverse;
    }

    /* Gentle organic wobble animations */
    @keyframes wobble1 {
        0%   { border-radius: 72% 28% 60% 40% / 45% 55% 45% 55%; transform: scale(1)   rotate(0deg);   }
        50%  { border-radius: 40% 60% 45% 55% / 60% 40% 55% 45%; transform: scale(1.05) rotate(4deg);  }
        100% { border-radius: 55% 45% 70% 30% / 35% 65% 40% 60%; transform: scale(0.97) rotate(-3deg); }
    }
    @keyframes wobble2 {
        0%   { border-radius: 40% 60% 35% 65% / 60% 40% 60% 40%; transform: scale(1)   rotate(0deg);   }
        50%  { border-radius: 60% 40% 55% 45% / 45% 55% 45% 55%; transform: scale(1.06) rotate(-5deg); }
        100% { border-radius: 30% 70% 50% 50% / 55% 45% 60% 40%; transform: scale(0.96) rotate(3deg);  }
    }
    @keyframes wobble3 {
        0%   { border-radius: 55% 45% 70% 30% / 40% 60% 40% 60%; transform: scale(1)   rotate(0deg);   }
        50%  { border-radius: 70% 30% 40% 60% / 60% 40% 50% 50%; transform: scale(1.04) rotate(6deg);  }
        100% { border-radius: 45% 55% 55% 45% / 30% 70% 30% 70%; transform: scale(0.98) rotate(-4deg); }
    }

    /* Make all content sit above the blobs */
    .stApp > * { position: relative; z-index: 1; }

    /* ── FLAG IMAGE STYLING ── */
    .flag-img {
        width: 36px;
        height: 24px;
        object-fit: cover;
        border-radius: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.18);
        margin-bottom: 4px;
        display: block;
    }

    /* ── CARD PANELS for sections ── */
    .market-card {
        background: rgba(255,255,255,0.70);
        backdrop-filter: blur(12px);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    }
    </style>

    <!-- Inject the blob divs into the page -->
    <div class="blob-container">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
        <div class="blob blob-4"></div>
        <div class="blob blob-5"></div>
        <div class="blob blob-6"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.title("Morning Market Digest")
st.caption(f"Last updated: {datetime.now().strftime('%A, %d %B %Y')}")

st.sidebar.title("Morning Market Digest")
st.sidebar.write("Simple overview of markets and news.")

# ── FLAG HELPER ────────────────────────────────────────────────────────────────
# flagcdn.com is a free, no-signup CDN for country flag images.
# Format: https://flagcdn.com/w40/{country_code}.png
def flag_html(country_code: str) -> str:
    """Return an <img> tag for a country flag from flagcdn.com."""
    url = f"https://flagcdn.com/w40/{country_code.lower()}.png"
    return f'<img src="{url}" class="flag-img" alt="{country_code} flag">'

# Map each ticker to its ISO 3166-1 alpha-2 country code
TICKER_FLAGS = {
    "^GSPC":  "us",   # S&P 500   → United States
    "^STOXX": "eu",   # EuroStoxx → European Union  (flagcdn supports 'eu')
    "^HSI":   "hk",   # Hang Seng → Hong Kong
    "^N225":  "jp",   # Nikkei    → Japan
    "^KS200": "kr",   # KOSPI     → South Korea
}

# ── DATA FETCHING ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def get_headlines():
    feed = feedparser.parse("https://www.cnbc.com/id/100727362/device/rss/rss.html")
    return [(entry.title, entry.link) for entry in feed.entries[:6]]

@st.cache_data(ttl=300)
def get_all_indices():
    tickers = ["^GSPC", "^STOXX", "^HSI", "^N225", "^KS200"]
    data = yf.download(tickers, period="5d", group_by="ticker", auto_adjust=True)
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
            results[ticker] = (round(float(last), 2), round(float(change), 2))
        except Exception:
            results[ticker] = (None, None)
    return results

# ── FORMAT HELPERS ─────────────────────────────────────────────────────────────
def format_price(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "N/A"
    return f"{x:.2f}"

def format_change(x):
    """Return a signed percentage string, e.g. '+1.23%' or '-0.45%'."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None          # None makes st.metric show no delta
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.2f}%"

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
headlines = get_headlines()
results   = get_all_indices()

# ── NEWS SECTION ───────────────────────────────────────────────────────────────
st.subheader("Top News")
for title, link in headlines:
    st.markdown(f"- [{title}]({link})")

# ── MARKETS SECTION ────────────────────────────────────────────────────────────
st.subheader("Global Markets")

INDICES = [
    ("^GSPC",  "S&P 500"),
    ("^STOXX", "EuroStoxx 600"),
    ("^HSI",   "Hang Seng"),
    ("^N225",  "Nikkei 225"),
    ("^KS200", "KOSPI 200"),
]

cols = st.columns(5)
for col, (ticker, label) in zip(cols, INDICES):
    price, change = results[ticker]
    with col:
        # Render the flag image above the metric
        st.markdown(flag_html(TICKER_FLAGS[ticker]), unsafe_allow_html=True)
        st.metric(label, format_price(price), format_change(change))

# ── BEGINNER HELP BOX ──────────────────────────────────────────────────────────
with st.expander("💡 What does this mean?"):
    st.write("""
    - **Price** = the current level of the index
    - **% change** = how much it moved since yesterday
    - 🟢 green arrow = the market went **up** today
    - 🔴 red arrow = the market went **down** today

    Don't worry if the numbers look big — indices measure thousands of stocks together!
    """)
