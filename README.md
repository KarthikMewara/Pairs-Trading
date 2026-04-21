## dev/creator = tubakhxn

# Pairs Trading Statistical Arbitrage System

This project is a quantitative trading system that implements a pairs trading (statistical arbitrage) strategy. It analyzes the spread between two correlated assets (such as stocks or cryptocurrencies), generates trading signals based on z-score thresholds, and visualizes the results with quant-style, visually dense graphs.

## What is this project about?
- **Pairs Trading**: A market-neutral trading strategy that exploits the mean-reverting behavior of the spread between two correlated assets.
- **Features**:
  - Synthetic or real data support
  - Spread and z-score calculation
  - Automated trading logic (long/short/exit)
  - Performance metrics (total return, Sharpe ratio, trade count)
  - Quantitative, dark-themed visualizations (spread, z-score, 3D scatter)

## How to fork and run
1. **Fork this repository** using the GitHub interface.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/your-forked-repo.git
   cd your-forked-repo
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # or manually:
   pip install pandas numpy matplotlib scikit-learn
   ```
4. **Run the project**:
   ```bash
   python main.py
   ```

## Relevant Wikipedia links
- [Pairs Trading](https://en.wikipedia.org/wiki/Pairs_trade)
- [Statistical Arbitrage](https://en.wikipedia.org/wiki/Statistical_arbitrage)
- [Sharpe Ratio](https://en.wikipedia.org/wiki/Sharpe_ratio)
- [Z-score](https://en.wikipedia.org/wiki/Standard_score)

---
Feel free to explore, modify, and extend the system for your own research or trading experiments!
