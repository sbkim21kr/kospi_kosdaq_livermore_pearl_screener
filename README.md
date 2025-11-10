# 📈 KOSPI–KOSDAQ Livermore Pearl Screener

A technical analysis dashboard inspired by **Jesse Livermore’s trading principles** and tailored for the Korean markets.  
This screener highlights potential "pearls" by combining **Volume Spike**, **Trend Arrow**, and a composite **Pearl Score**.

---

## 🚀 Features

- Automated **GitHub Actions workflow** runs every weekday after market close (17:30 KST).
- Fetches **all KOSPI + KOSDAQ stocks** using FinanceDataReader and PyKRX.
- Computes technical indicators (MA20, MA60, RSI, MACD, ATR, OBV).
- Generates a single canonical file: `output/latest.csv` with results.
- Saves fetch timestamp in `output/fetch_time.txt`.
- Streamlit dashboard displays:
  - Top 10 and Bottom 10 pearls.
  - Interactive filters (Volume Spike, Pearl Score, Trend Arrow).
  - Styled tables with arrows and star ratings.
  - Export filtered results as CSV.

---

## 📊 Pearl Score — How It Works

The **Pearl Score** is like a *health check* for a stock’s technical setup.  
It blends four dimensions into one number:

- **Market Attention (Volume Spike)**  
  Is the stock attracting unusual trading activity compared to its 20‑day average?

- **Trend Conviction (Trend Strength)**  
  Is the price moving with authority?  
  → Checks if the stock is above MA20, MA60, and if MACD is bullish.

- **Momentum Balance (Momentum Quality)**  
  Is the move sustainable?  
  → Uses RSI to reward balanced momentum (not overheated, not too weak).

- **Volatility Risk (Volatility Penalty)**  
  Is the ride too bumpy?  
  → Adjusts the score downward if ATR is high relative to price.

---

### 🧮 Formula (conceptual view)



\[
\text{PearlScore} = \frac{\text{Market Attention} \times \text{Trend Conviction} \times \text{Momentum Balance}}{\text{Volatility Risk}}
\]



---

### ⭐ Star Ratings

| Pearl Score Range | Rating   |
|-------------------|----------|
| ≥ 81              | ★★★★★    |
| ≥ 61              | ★★★★☆    |
| ≥ 41              | ★★★☆☆    |
| ≥ 21              | ★★☆☆☆    |
| > 0               | ★☆☆☆☆    |
| = 0               | ☆☆☆☆☆    |

---

## 🖥️ Dashboard

- Built with **Streamlit**.
- Shows **Top 10 / Bottom 10 pearls**.
- Interactive filters for custom screening.
- Styled tables with arrows and stars.
- Export filtered results as CSV with timestamped filenames.

---

## 🔄 Data Flow Diagram

```mermaid
flowchart TD
    A[GitHub Actions Scheduler - 17h30 KST weekdays] --> B[Run scanner.py - Fetch KOSPI and KOSDAQ data]
    B --> C[Compute Indicators - MA, RSI, MACD, ATR, OBV]
    C --> D[Generate output/latest.csv]
    C --> E[Write output/fetch_time.txt]
    D --> F[Streamlit Dashboard - Top and Bottom 10, Filters, Exports]
    E --> F
