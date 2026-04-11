import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd
from datetime import datetime
 
# ── PAGE SETTINGS ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Morning Market Digest", layout="centered")
 
# ── BACKGROUND BLOBS ───────────────────────────────────────────────────────────
#
# HOW THE BLOBS WORK (plain English):
#
#   1. Each blob is just a <div> (an invisible box) with:
#        - a colour
#        - a squished, wobbly shape (set by "border-radius")
#        - a position on the page (top/left as a % of the screen)
#        - a slow CSS animation that gently changes its shape over time
#
#   2. We define every blob as one line in the BLOBS list below.
#      Each line has:  (colour,  width, height,  top%,  left%,  animation speed in seconds)
#
#   3. A loop at the bottom turns each line into real HTML automatically,
#      so you never have to repeat yourself.
#
#   To ADD a blob:  add a new line to the BLOBS list.
#   To CHANGE a colour: edit the hex colour code (e.g. "#FF4ECD" = hot pink).
#   To MOVE a blob: change the top% and left% numbers (0 = top/left edge, 100 = bottom/right edge).
 
BLOBS = [
    # colour       width   height  top%   left%  speed(s)
    ("#FF4ECD",   "320px", "280px",  "-5",  "-8",    8),   # hot pink    — top-left corner
    ("#FFD93D",   "260px", "240px",  "-3",  "88",   10),   # yellow      — top-right corner
    ("#6CF0C2",   "360px", "300px",  "35",  "-10",  12),   # mint green  — middle-left edge
    ("#4FC3F7",   "280px", "260px",  "40",  "85",    9),   # sky blue    — middle-right edge
    ("#FF7043",   "240px", "220px",  "75",  "5",    11),   # coral       — bottom-left
    ("#B388FF",   "200px", "190px",  "80",  "82",    7),   # purple      — bottom-right
    ("#FFABAB",   "200px", "180px",  "42",  "30",    9),   # soft pink   — page centre-left
    ("#A8D8EA",   "180px", "160px",  "50",  "55",   11),   # pale blue   — page centre-right
    ("#B5EAD7",   "160px", "150px",  "58",  "42",    8),   # mint        — page centre-bottom
]
 
# Build one CSS block + one <div> per blob using a loop.
# (You don't need to touch anything below this line to customise blobs!)
blob_css   = ""   # will hold all the CSS rules
blob_divs  = ""   # will hold all the <div> tags
 
for i, (colour, width, height, top, left, speed) in enumerate(BLOBS):
    blob_name = f"blob-{i}"
    blob_css += f"""
    #{blob_name} {{
        position: absolute;
        width: {width}; height: {height};
        background: {colour};
        top: {top}%; left: {left}%;
        border-radius: 60% 40% 55% 45% / 50% 60% 40% 50%;  /* squished circle shape */
        opacity: 0.55;                                        /* slightly see-through */
        animation: wobble {speed}s ease-in-out infinite alternate; /* slow shape-shift */
    }}
    """
    blob_divs += f'<div id="{blob_name}"></div>\n'
 
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');
 
    .stApp {{
        background-color: #f0f6ff;
        font-family: 'Nunito', sans-serif;
    }}
 
    /* The blob container sits behind everything else on the page */
    #blob-container {{
        position: fixed;   /* stays in place even when you scroll */
        inset: 0;          /* covers the full screen */
        z-index: 0;        /* behind all content */
        pointer-events: none;   /* clicks pass straight through it */
        overflow: hidden;
    }}
 
    /* All content sits on top of the blobs */
    .stApp > * {{ position: relative; z-index: 1; }}
 
    /* The wobble animation: slowly shifts the blob's shape */
    @keyframes wobble {{
        0%   {{ border-radius: 60% 40% 55% 45% / 50% 60% 40% 50%; transform: scale(1);    }}
        50%  {{ border-radius: 40% 60% 45% 55% / 60% 40% 55% 45%; transform: scale(1.05); }}
        100% {{ border-radius: 55% 45% 65% 35% / 35% 65% 40% 60%; transform: scale(0.97); }}
    }}
 
    /* Individual blob styles (auto-generated from the BLOBS list above) */
    {blob_css}
 
    /* Flag images above each market metric */
    .flag-img {{
        width: 36px; height: 24px;
        object-fit: cover;
        border-radius: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.18);
        margin-bottom: 4px;
        display: block;
    }}
 
    /* Semi-transparent card panels so blobs show through softly */
    .market-card {{
        background: rgba(255,255,255,0.70);
        backdrop-filter: blur(12px);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    }}
    </style>
 
    <div id="blob-container">
        {blob_divs}
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
    "^STOXX": "eu",   # EuroStoxx → European Union
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
st.markdown('<div class="market-card">', unsafe_allow_html=True)
st.subheader("📰 Top News")
for title, link in headlines:
    st.markdown(f"- [{title}]({link})")
st.markdown('</div>', unsafe_allow_html=True)
 
# ── MARKETS SECTION ────────────────────────────────────────────────────────────
st.markdown('<div class="market-card">', unsafe_allow_html=True)
st.subheader("🌍 Global Markets")
 
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
 
st.markdown('</div>', unsafe_allow_html=True)
 
# ── BEGINNER HELP BOX ──────────────────────────────────────────────────────────
with st.expander("💡 What does this mean?"):
    st.write("""
    - **Price** = the current level of the index
    - **% change** = how much it moved since yesterday
    - 🟢 green arrow = the market went **up** today
    - 🔴 red arrow = the market went **down** today
 
    Don't worry if the numbers look big — indices measure thousands of stocks together!
    """)
