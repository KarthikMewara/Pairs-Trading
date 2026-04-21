import pandas as pd
import numpy as np

def generate_signals(zscore: pd.Series, entry_threshold: float = 2.0, exit_threshold: float = 0.1) -> pd.DataFrame:
    """
    Generates trading signals and maintains position state based on z-score thresholds.
    """
    signals = pd.DataFrame(index=zscore.index)
    signals['zscore'] = zscore
    signals['signal'] = 0
    
    # 1. Entry Logic: The spread has deviated too far from the mean
    signals.loc[zscore > entry_threshold, 'signal'] = -1  # Short the spread
    signals.loc[zscore < -entry_threshold, 'signal'] = 1  # Long the spread
    
    # Forward fill the position so we hold it open
    signals['position'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
    
    # 2. Exit Logic: The spread has snapped back to normal (near zero)
    signals.loc[(signals['position'] == 1) & (zscore > -exit_threshold) & (zscore < exit_threshold), 'position'] = 0
    signals.loc[(signals['position'] == -1) & (zscore > -exit_threshold) & (zscore < exit_threshold), 'position'] = 0
    
    # Forward fill again to lock in the flat (0) state after exiting
    signals['position'] = signals['position'].replace(0, np.nan).ffill().fillna(0)
    
    return signals

def compute_performance(df: pd.DataFrame) -> dict:
    """
    Computes total return, number of trades, and Sharpe ratio.
    """
    if 'profit' not in df.columns:
        return {}
        
    total_return = df['profit'].sum()
    
    # Count trades by looking at when the signal changes (ignoring exits)
    num_trades = ((df['signal'].diff().abs() > 0) & (df['signal'] != 0)).sum()
    
    # Annualized Sharpe Ratio calculation
    sharpe = 0
    if df['profit'].std(ddof=0) > 0:
        sharpe = df['profit'].mean() / df['profit'].std(ddof=0) * (252 ** 0.5)
        
    return {
        'Total Return': round(total_return, 4),
        'Number of Trades': int(num_trades),
        'Sharpe Ratio': round(sharpe, 4)
    }

# --- TEST BLOCK ---
if __name__ == "__main__":
    from data import fetch_pairs_data
    from spread import compute_spread, compute_zscore
    
    print("Fetching test data for AAPL and MSFT...")
    df = fetch_pairs_data('AAPL', 'MSFT', '2023-01-01', '2024-01-01')
    
    # Run the Math
    df['spread'] = compute_spread(df)
    df['zscore'] = compute_zscore(df['spread'], window=30)
    
    # Run the Logic
    signals = generate_signals(df['zscore'], entry_threshold=2.0)
    
    # Combine everything to calculate simulated profits
    df = pd.concat([df, signals[['signal', 'position']]], axis=1)
    
    # Calculate daily profit: If we held a position yesterday, multiply it by today's change in spread
    df['profit'] = df['position'].shift(1).fillna(0) * df['spread'].diff().fillna(0)
    
    perf = compute_performance(df)
    
    print("\n--- Performance Summary ---")
    for k, v in perf.items():
        print(f"{k}: {v}")