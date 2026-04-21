import streamlit as st
import datetime
import pandas as pd
import requests
import io
from data import fetch_pairs_data
from spread import compute_spread, compute_zscore
from strategy import generate_signals, compute_performance
from visualization import plot_2d_charts, plot_3d_scatter

st.set_page_config(layout="wide", page_title="Pairs Trading Engine")

# --- DYNAMIC ASSET DICTIONARY ---
@st.cache_data(ttl=86400)
def fetch_live_tickers():
    """Dynamically scrapes the S&P 500 and Nifty 50 constituents."""
    tickers_dict = {}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    with st.spinner("Fetching live market indices (S&P 500 & Nifty 50)..."):
        try:
            # 1. Fetch S&P 500
            sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            sp500_html = requests.get(sp500_url, headers=headers).text
            sp500_tables = pd.read_html(io.StringIO(sp500_html))
            
            for table in sp500_tables:
                if 'Symbol' in table.columns and 'Security' in table.columns:
                    us_dict = dict(zip(table['Symbol'], table['Security']))
                    tickers_dict.update(us_dict)
                    break 
            
            # 2. Fetch Nifty 50
            nifty_url = 'https://en.wikipedia.org/wiki/NIFTY_50'
            nifty_html = requests.get(nifty_url, headers=headers).text
            nifty_tables = pd.read_html(io.StringIO(nifty_html))
            
            for table in nifty_tables:
                if 'Symbol' in table.columns and 'Company Name' in table.columns:
                    for _, row in table.iterrows():
                        symbol = f"{row['Symbol']}.NS"
                        tickers_dict[symbol] = row['Company Name']
                    break 
                
            return tickers_dict
            
        except Exception as e:
            st.warning(f"Failed to fetch live tickers: {e}")
            return {"AAPL": "Apple Inc.", "MSFT": "Microsoft", "GOOGL": "Alphabet", "RELIANCE.NS": "Reliance"}

# Execute the dynamic scraper
AVAILABLE_ASSETS = fetch_live_tickers()
AVAILABLE_ASSETS.update({
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "GC=F": "Gold Futures (XAU/USD)",
    "SI=F": "Silver Futures",
    "CL=F": "Crude Oil (WTI)",
    "NG=F": "Natural Gas"
})
display_options = [f"{ticker} ({name})" for ticker, name in AVAILABLE_ASSETS.items()]

# Set smart defaults (Apple and Microsoft are highly correlated tech stocks)
try:
    default_idx_1 = [i for i, opt in enumerate(display_options) if "AAPL" in opt][0]
    default_idx_2 = [i for i, opt in enumerate(display_options) if "MSFT" in opt][0]
except IndexError:
    default_idx_1, default_idx_2 = 0, 1

# --- UI CONTROLS (Sidebar) ---
st.sidebar.header("Pairs Selection")
selected_opt_1 = st.sidebar.selectbox("Asset 1 (Base)", display_options, index=default_idx_1)
selected_opt_2 = st.sidebar.selectbox("Asset 2 (Compare)", display_options, index=default_idx_2)

sym1 = selected_opt_1.split(" ")[0]
sym2 = selected_opt_2.split(" ")[0]

st.sidebar.markdown("---")
st.sidebar.header("Strategy Parameters")
interval = st.sidebar.selectbox("Timeframe", ["1d", "1wk", "1h", "15m", "5m"])
window = st.sidebar.slider("Z-Score Rolling Window", min_value=10, max_value=100, value=30)
entry_threshold = st.sidebar.slider("Entry Z-Score Threshold", min_value=1.0, max_value=4.0, value=2.0, step=0.1)
exit_threshold = st.sidebar.slider("Exit Z-Score Threshold", min_value=0.0, max_value=1.0, value=0.1, step=0.05)

# --- DYNAMIC DATE LOGIC ---
end_date = datetime.date.today()
if interval in ["1h", "15m", "5m"]:
    start_date = end_date - datetime.timedelta(days=59)
elif interval == "1wk":
    start_date = end_date - datetime.timedelta(days=365 * 3)
else:
    start_date = end_date - datetime.timedelta(days=365 * 2)

start_str = start_date.strftime('%Y-%m-%d')
end_str = end_date.strftime('%Y-%m-%d')

# --- EXECUTION ---
if sym1 == sym2:
    st.error("Please select two different assets to compute a spread.")
else:
    with st.spinner(f"Crunching {interval} data for {sym1} vs {sym2}..."):
        # 1. Fetch & Align Data
        df = fetch_pairs_data(sym1, sym2, start=start_str, end=end_str, interval=interval)
        
        # 2. Run Math
        df['spread'] = compute_spread(df)
        df['zscore'] = compute_zscore(df['spread'], window=window)
        
        # 3. Run Logic
        signals = generate_signals(df['zscore'], entry_threshold=entry_threshold, exit_threshold=exit_threshold)
        df = pd.concat([df, signals[['signal', 'position']]], axis=1)
        
        # Calculate daily profit based on spread differential
        df['profit'] = df['position'].shift(1).fillna(0) * df['spread'].diff().fillna(0)
        
        # 4. Metrics
        metrics = compute_performance(df)

    # --- UI RENDERING (Main Page) ---
    st.title(f"Statistical Arbitrage: {sym1} vs {sym2} ({interval})")

    if metrics:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Return (Spread Points)", metrics.get('Total Return', 0))
        col2.metric("Sharpe Ratio", metrics.get('Sharpe Ratio', 0))
        col3.metric("Total Trades", metrics.get('Number of Trades', 0))

    # Render Plotly Charts
    st.markdown("### Time Series Analysis")
    fig2d = plot_2d_charts(df, entry_threshold=entry_threshold)
    st.plotly_chart(fig2d, use_container_width=True)

    st.markdown("### 3D Profitability Topography")
    fig3d = plot_3d_scatter(df)
    st.plotly_chart(fig3d, use_container_width=True)