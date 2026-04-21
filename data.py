import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_pairs_data(symbol1: str, symbol2: str, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
    """
    Fetches historical data for two assets and aligns their closing prices.
    """
    print(f"Fetching {interval} data for {symbol1} and {symbol2} from {start} to {end}...")
    
    # Download both assets
    df1 = yf.download(symbol1, start=start, end=end, interval=interval)
    df2 = yf.download(symbol2, start=start, end=end, interval=interval)
    
    if df1.empty or df2.empty:
        raise ValueError("Failed to fetch data for one or both symbols. Check tickers or dates.")
        
    # Flatten MultiIndex columns if yfinance returns them
    if isinstance(df1.columns, pd.MultiIndex):
        df1.columns = df1.columns.get_level_values(0)
    if isinstance(df2.columns, pd.MultiIndex):
        df2.columns = df2.columns.get_level_values(0)
        
    # Create a new DataFrame with aligned closing prices
    # We use .dropna() to remove any days where one stock traded but the other didn't (e.g., trading halts)
    combined_df = pd.DataFrame({
        'asset1': df1['Close'],
        'asset2': df2['Close']
    }).dropna()
    
    return combined_df

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Let's test with two highly correlated tech stocks
    sym1 = 'AAPL'
    sym2 = 'MSFT'
    
    print("--- Testing Pairs Data Fetcher ---")
    df = fetch_pairs_data(sym1, sym2, start='2023-01-01', end='2024-01-01')
    
    print("\nFirst 5 rows of perfectly aligned data:")
    print(df.head())
    print(f"\nTotal aligned trading days: {len(df)}")