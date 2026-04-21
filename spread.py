import pandas as pd
import numpy as np

def compute_spread(df: pd.DataFrame) -> pd.Series:
    """
    Computes the raw price spread between asset1 and asset2.
    """
    return df['asset1'] - df['asset2']

def compute_zscore(spread: pd.Series, window: int = 30) -> pd.Series:
    """
    Computes rolling z-score of the spread to identify over-extended divergences.
    """
    mean = spread.rolling(window=window, min_periods=1).mean()
    std = spread.rolling(window=window, min_periods=1).std(ddof=0)
    
    # Calculate Z-score, replacing 0 standard deviation with NaN to prevent division by zero crashes
    zscore = (spread - mean) / std.replace(0, np.nan)
    return zscore