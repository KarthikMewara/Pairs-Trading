import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_2d_charts(df: pd.DataFrame, entry_threshold: float = 2.0):
    """
    Plots the Spread and Z-Score in an interactive 2-tier dashboard.
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.08,
                        row_heights=[0.5, 0.5],
                        subplot_titles=("Spread (Asset 1 - Asset 2)", "Z-Score & Trading Signals"))

    # --- 1. SPREAD CHART ---
    fig.add_trace(go.Scatter(x=df.index, y=df['spread'], mode='lines', name='Spread', 
                             line=dict(color='#00FFAA', width=1.5)), row=1, col=1)

    # --- 2. Z-SCORE OSCILLATOR ---
    fig.add_trace(go.Scatter(x=df.index, y=df['zscore'], mode='lines', name='Z-Score', 
                             line=dict(color='#FFCC00', width=1.5)), row=2, col=1)
    
    # Add Threshold Lines
    fig.add_hline(y=entry_threshold, line_dash="dash", line_color="#FF3366", row=2, col=1, annotation_text="Short Spread")
    fig.add_hline(y=-entry_threshold, line_dash="dash", line_color="#33CCFF", row=2, col=1, annotation_text="Long Spread")
    fig.add_hline(y=0, line_dash="dot", line_color="#ffffff", opacity=0.3, row=2, col=1)

    # Add Buy/Sell Markers if signals exist
    if 'signal' in df.columns:
        longs = df[df['signal'] == 1]
        shorts = df[df['signal'] == -1]
        
        if not longs.empty:
            fig.add_trace(go.Scatter(x=longs.index, y=longs['zscore'], mode='markers', name='Long Trigger', 
                                     marker=dict(symbol='triangle-up', color='#33CCFF', size=12, line=dict(color='black', width=1))), row=2, col=1)
        if not shorts.empty:
            fig.add_trace(go.Scatter(x=shorts.index, y=shorts['zscore'], mode='markers', name='Short Trigger', 
                                     marker=dict(symbol='triangle-down', color='#FF3366', size=12, line=dict(color='black', width=1))), row=2, col=1)

    # --- LAYOUT & STYLING ---
    fig.update_layout(
        height=600, template="plotly_dark", plot_bgcolor='#181a20', paper_bgcolor='#181a20',
        hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20), showlegend=True
    )
    fig.update_xaxes(showgrid=False, showspikes=True, spikemode='across', spikesnap='cursor', spikedash='solid', spikecolor='#ffffff', spikethickness=1)
    fig.update_yaxes(showgrid=False)

    return fig

def plot_3d_scatter(df: pd.DataFrame):
    """
    Plots an interactive 3D scatter: X=spread, Y=z-score, Z=profit, with gradient colors.
    """
    df = df.copy()
    if 'profit' not in df.columns:
        df['profit'] = 0
    df['cum_profit'] = df['profit'].cumsum()

    fig = go.Figure(data=[go.Scatter3d(
        x=df['spread'],
        y=df['zscore'],
        z=df['cum_profit'],
        mode='markers',
        marker=dict(
            size=5,
            color=df['cum_profit'], # Color scale driven by cumulative profit
            colorscale='Plasma',
            opacity=0.8,
            colorbar=dict(title="Profit")
        ),
        text=df.index.astype(str),
        hovertemplate="<b>Date:</b> %{text}<br><b>Spread:</b> %{x:.2f}<br><b>Z-Score:</b> %{y:.2f}<br><b>Cum Profit:</b> %{z:.2f}<extra></extra>"
    )])

    fig.update_layout(
        title="3D Trade Analysis: Spread vs Z-Score vs Cumulative Profit",
        scene=dict(
            xaxis_title='Spread',
            yaxis_title='Z-Score',
            zaxis_title='Cumulative Profit',
            bgcolor='#181a20',
            xaxis=dict(showgrid=True, gridcolor='#333333'),
            yaxis=dict(showgrid=True, gridcolor='#333333'),
            zaxis=dict(showgrid=True, gridcolor='#333333')
        ),
        height=700,
        template="plotly_dark",
        paper_bgcolor='#181a20',
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

# --- TEST BLOCK ---
if __name__ == "__main__":
    from data import fetch_pairs_data
    from spread import compute_spread, compute_zscore
    from strategy import generate_signals
    
    print("Fetching data and calculating logic...")
    df = fetch_pairs_data('AAPL', 'MSFT', '2023-01-01', '2024-01-01')
    df['spread'] = compute_spread(df)
    df['zscore'] = compute_zscore(df['spread'], window=30)
    signals = generate_signals(df['zscore'], entry_threshold=2.0)
    df = pd.concat([df, signals[['signal', 'position']]], axis=1)
    df['profit'] = df['position'].shift(1).fillna(0) * df['spread'].diff().fillna(0)
    
    print("Rendering Interactive Plotly Charts in your browser...")
    fig2d = plot_2d_charts(df, entry_threshold=2.0)
    fig3d = plot_3d_scatter(df)
    
    # This will open two tabs in your default web browser
    fig2d.show()
    fig3d.show()