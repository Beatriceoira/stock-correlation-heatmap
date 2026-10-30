# Stock Correlation Heatmap

A beginner-friendly Python tool that measures how stocks move relative to each other, shows the result as a color-coded heatmap, and points out which pairs would help diversify a portfolio.

---

## Purpose

When you hold several stocks, owning many of them does not automatically reduce risk. If they all rise and fall together, a bad day hits everything at once. This project answers a simple question:

> **Which of my stocks move together, and which ones don't?**

It lets you:

- Analyze relationships between stocks
- Generate a correlation matrix
- Visualize the matrix as a heatmap
- Identify diversification opportunities (low-correlation pairs)

---

## Concepts

### 1. Returns, not prices
Prices trend upward or downward over time, and two unrelated stocks that both happen to trend up will look "correlated". To avoid this, the script converts prices into **daily returns** (the percentage change from one day to the next) and correlates those instead.

```
return_today = (price_today - price_yesterday) / price_yesterday
```

### 2. Correlation (statistics)
The **Pearson correlation coefficient** measures how strongly two series move together. It always falls between -1 and +1:

| Value | Meaning | Diversification |
|-------|---------|-----------------|
| +1.0  | Move perfectly together | None |
| +0.7 to +1.0 | Strongly related (often the same sector) | Poor |
| +0.3 to +0.7 | Moderately related | Moderate |
| 0 to +0.3 | Mostly unrelated | Good |
| Negative | Tend to move in opposite directions | Excellent (rare between stocks) |

### 3. The correlation matrix (linear algebra)
With N stocks, the results form an **N x N symmetric matrix**:

- The diagonal is always 1.0 (a stock is perfectly correlated with itself).
- The matrix is symmetric: correlation(A, B) = correlation(B, A).
- Each cell is the correlation between the row stock and the column stock.

Under the hood this is the covariance matrix rescaled by each stock's standard deviation. Pandas computes it in one call: `returns.corr()`.

### 4. Diversification
Portfolio risk depends on how assets move *together*, not just on how risky each one is. Combining assets with low correlation smooths out the overall ups and downs. That is why the script highlights the lowest-correlation pairs.

---

## How the code works

Everything lives in `stock_correlation_heatmap.py`.

| Function | What it does |
|----------|--------------|
| `load_prices(tickers, years)` | Downloads adjusted closing prices from Yahoo Finance using `yfinance`. Drops tickers with missing data. |
| `simulate_prices(tickers, years)` | Generates fake prices with realistic sector clusters. Used by `--demo` so the project runs without internet. |
| `correlation_matrix(prices)` | Converts prices to daily returns with `pct_change()`, then builds the matrix with `.corr()`. |
| `plot_heatmap(corr, path)` | Draws the matrix with matplotlib: green means low correlation (good for diversifying), red means high. Each cell shows its value. |
| `pair_table(corr)` | Lists every unique pair and sorts by correlation, so the best and worst pairs are easy to read. |
| `main()` | Parses command-line options, runs the steps above, and prints the report. |

### Output files

- `correlation_matrix.csv`: the full matrix, ready to open in Excel
- `correlation_heatmap.png`: the heatmap image
- Terminal report: best diversifiers, most similar pairs, and each stock's average correlation to the rest of the basket

---

## Setup

**Requirements:** Python 3.9 or newer.

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<stock-correlation-heatmap>.git
cd <stock-correlation-heatmap>

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Default basket of 12 stocks, last 2 years
python stock_correlation_heatmap.py

# Your own tickers and time window
python stock_correlation_heatmap.py --tickers AAPL MSFT XOM JPM KO --years 3

# Save the image under a different name
python stock_correlation_heatmap.py --out my_heatmap.png

# Offline demo using simulated data
python stock_correlation_heatmap.py --demo
```

| Option | Default | Description |
|--------|---------|-------------|
| `--tickers` | 12 large US stocks and GLD | Space-separated ticker symbols |
| `--years` | `2` | How many years of history to download |
| `--out` | `correlation_heatmap.png` | Output image filename |
| `--demo` | off | Use simulated data instead of downloading |

### Reading the results

- **Dark red blocks** on the heatmap are stocks that move almost as one, usually same-sector (for example MSFT and GOOGL). Holding both adds little diversification.
- **Green or light cells** are pairs that behave differently. Those are your diversification candidates.
- In the "average correlation" list, **lower is better**: that stock adds the most diversification to the basket.

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'yfinance'` (or pandas, matplotlib) | Dependencies not installed, or the wrong Python environment is active | Activate your virtual environment, then run `pip install -r requirements.txt` |
| `pip` or `python` not found | Python not on your PATH | Try `python3` and `pip3`, or reinstall Python and tick "Add to PATH" |
| Empty data, `No data found`, or `Too Many Requests` errors | Yahoo Finance is rate limiting you or temporarily down | Wait a few minutes and retry. Run `pip install --upgrade yfinance` since Yahoo changes often. |
| A ticker is missing from the heatmap | The symbol is wrong or has no price history (the script drops it) | Check the symbol on finance.yahoo.com. Non-US stocks need a suffix, such as `.L` for London or `.PS` for Philippines. |
| `KeyError: 'Close'` | An older or newer yfinance version returns a different column layout | Upgrade with `pip install --upgrade yfinance` |
| Very few stocks, or a tiny matrix | A recently listed stock forces all dates to be trimmed | Lower `--years` or remove the new ticker |
| SSL or connection errors | Network, proxy, or firewall blocking Yahoo | Try another network or turn off the VPN. Use `--demo` to confirm the rest of the code works. |
| Heatmap window does not open | The script saves the image to a file instead of opening a window | Open `correlation_heatmap.png` from the folder |
| Overlapping or cut-off labels | Too many tickers for the figure size | Use fewer tickers, or increase `figsize` in `plot_heatmap` |
| Stuck on the first check | Unsure whether the problem is your setup or the data | Run `--demo`. If it works, the code is fine and the issue is network or Yahoo. |

---

## Limitations

- **Past correlations are not guarantees.** They shift over time and often rise sharply during market crashes, exactly when you need diversification most.
- Correlation only captures **linear** relationships.
- Results depend on the **time window** you pick. Try several.
- Demo mode uses simulated data and does not reflect real markets.
- This is an educational project, **not financial advice**.

## Ideas for extending it

- Rolling correlations (for example a 60-day window) to see how relationships change
- Hierarchical clustering to group similar stocks automatically
- Portfolio variance calculations using the covariance matrix
- Support for crypto, bonds, and international ETFs

## License

MIT 

