import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_pairs_data(symbol1: str, symbol2: str, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
    """
    Fetches historical data for two assets and aligns their closing prices.
    """
    print(f"Fetching {interval} data for {symbol1} and {symbol2} from {start} to {end}...")
    
    # FIX 1: Wikipedia formats tickers like Berkshire Hathaway as BRK.B, but Yahoo expects BRK-B. 
    # We replace the dot with a dash, unless it's an Indian stock (.NS) which actually needs the dot.
    symbol1 = symbol1.replace('.', '-') if '.NS' not in symbol1 else symbol1
    symbol2 = symbol2.replace('.', '-') if '.NS' not in symbol2 else symbol2

    # FIX 2: Use Ticker().history() instead of download() for much better reliability on Streamlit Cloud
    tkr1 = yf.Ticker(symbol1)
    tkr2 = yf.Ticker(symbol2)
    
    df1 = tkr1.history(start=start, end=end, interval=interval)
    df2 = tkr2.history(start=start, end=end, interval=interval)
    
    if df1.empty or df2.empty:
        failed_syms = []
        if df1.empty: failed_syms.append(symbol1)
        if df2.empty: failed_syms.append(symbol2)
        raise ValueError(f"Yahoo Finance returned empty data for: {', '.join(failed_syms)}. Check if the ticker is valid or if the market was closed.")
        
    # FIX 3: Strip timezones from the data. 
    # If you pair a US stock and an Indian stock, their timezones won't match and pandas will crash.
    df1.index = pd.to_datetime(df1.index).tz_localize(None)
    df2.index = pd.to_datetime(df2.index).tz_localize(None)
        
    # Create a new DataFrame with aligned closing prices
    # .dropna() ensures we only trade on days where BOTH markets were open
    combined_df = pd.DataFrame({
        'asset1': df1['Close'],
        'asset2': df2['Close']
    }).dropna()
    
    if combined_df.empty:
        raise ValueError(f"Data fetched successfully, but the dates did not overlap between {symbol1} and {symbol2}. Ensure you aren't mixing intraday timeframes across different global timezones.")
    
    return combined_df

# --- TEST BLOCK ---
if __name__ == "__main__":
    sym1 = 'AAPL'
    sym2 = 'MSFT'
    
    print("--- Testing Pairs Data Fetcher ---")
    df = fetch_pairs_data(sym1, sym2, start='2023-01-01', end='2024-01-01')
    
    print("\nFirst 5 rows of perfectly aligned data:")
    print(df.head())
    print(f"\nTotal aligned trading days: {len(df)}")