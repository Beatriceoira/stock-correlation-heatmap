"""
Stock Correlation Heatmap
-------------------------
1. Download (or simulate) daily prices for a set of stocks
2. Convert prices to daily returns
3. Build a correlation matrix
4. Plot it as a heatmap
5. Report the best diversification pairs (lowest correlation)

Usage:
    pip install yfinance pandas numpy matplotlib
    python stock_correlation_heatmap.py                      # real data via Yahoo Finance
    python stock_correlation_heatmap.py --tickers AAPL MSFT XOM JPM --years 3
    python stock_correlation_heatmap.py --demo               # simulated data, no internet needed
"""
import argparse
import itertools

import matplotlib
import numpy as np
import pandas as pd

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM", "BAC",
                   "XOM", "CVX", "JNJ", "PFE", "KO", "GLD"]


def load_prices(tickers, years):
    import yfinance as yf
    data = yf.download(tickers, period=f"{years}y", auto_adjust=True, progress=False)["Close"]
    return data.dropna(how="all").dropna(axis=1)


def simulate_prices(tickers, years, seed=42):
    """Fake prices with sector structure, so the heatmap shows realistic clusters."""
    rng = np.random.default_rng(seed)
    n = 252 * years
    sectors = {"tech": ["AAPL", "MSFT", "GOOGL", "AMZN"], "fin": ["JPM", "BAC"],
               "energy": ["XOM", "CVX"], "health": ["JNJ", "PFE"]}
    market = rng.normal(0.0004, 0.01, n)
    sector_f = {s: rng.normal(0, 0.008, n) for s in sectors}
    cols = {}
    for t in tickers:
        sec = next((s for s, m in sectors.items() if t in m), None)
        beta = 0.3 if sec is None else 1.0
        r = beta * market + (sector_f[sec] if sec else 0) + rng.normal(0, 0.006, n)
        cols[t] = 100 * np.exp(np.cumsum(r))
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    return pd.DataFrame(cols, index=idx)


def correlation_matrix(prices):
    returns = prices.pct_change().dropna()   # correlate returns, not prices
    return returns.corr()


def plot_heatmap(corr, path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(corr.values, cmap="RdYlGn_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr)), corr.index)
    for i in range(len(corr)):
        for j in range(len(corr)):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if abs(v) > 0.75 else "black")
    fig.colorbar(im, ax=ax, label="Correlation of daily returns")
    ax.set_title("Stock Correlation Heatmap\n(green = diversifies, red = moves together)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Saved heatmap -> {path}")


def pair_table(corr):
    pairs = [(a, b, corr.loc[a, b]) for a, b in itertools.combinations(corr.columns, 2)]
    return pd.DataFrame(pairs, columns=["A", "B", "corr"]).sort_values("corr")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    p.add_argument("--years", type=int, default=2)
    p.add_argument("--demo", action="store_true", help="use simulated data")
    p.add_argument("--out", default="correlation_heatmap.png")
    a = p.parse_args()

    matplotlib.use("Agg")
    prices = simulate_prices(a.tickers, a.years) if a.demo else load_prices(a.tickers, a.years)
    corr = correlation_matrix(prices)
    corr.round(3).to_csv("correlation_matrix.csv")

    pairs = pair_table(corr)
    print("\nBest diversifiers (lowest correlation):")
    print(pairs.head(5).round(2).to_string(index=False))
    print("\nMost similar (highest correlation, avoid holding both):")
    print(pairs.tail(5).iloc[::-1].round(2).to_string(index=False))

    avg = (corr.sum() - 1) / (len(corr) - 1)
    print("\nAverage correlation to the rest of the basket (lower = better diversifier):")
    print(avg.sort_values().round(2).to_string())

    plot_heatmap(corr, a.out)


if __name__ == "__main__":
    main()
