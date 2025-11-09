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

## 📊 Pearl Score Explained

The **Pearl Score** is a composite metric designed to highlight stocks with strong technical setups. It combines **volume dynamics, trend strength, momentum quality, and volatility adjustment**.

### 1. 🔥 Volume Spike
- **Definition**: Ratio of today’s trading volume to the 20‑day average volume.
- **Formula**:  
  

\[
  \text{VolumeSpike} = \frac{\text{Daily Volume}}{\text{20‑day Average Volume}}
  \]



### 2. ➡️ Trend Arrow
- **Definition**: Short‑term trend indicator based on the 5‑day moving average.
- **Logic**:
  - Closing price ≈ MA5 (±0.2%) → `→` (sideways)
  - Closing price > MA5 → `↑` (uptrend)
  - Closing price < MA5 → `↓` (downtrend)

### 3. 📐 Technical Signals
- MA20 / MA60 → medium & long‑term trend
- RSI(14) → momentum oscillator
- MACD vs Signal → trend confirmation
- ATR → volatility measure
- OBV → volume‑based momentum

### 4. 💎 Pearl Score Calculation


\[
\text{PearlScore} = \frac{\text{VolumeSpike} \times \text{TrendStrength} \times \text{MomentumQuality}}{\text{VolatilityPenalty}}
\]



- **Trend Strength**: 1 + 0.2 × (bullish signals: price > MA20, price > MA60, MACD > Signal)  
- **Momentum Quality**: 1 − |RSI − 50| / 50  
- **Volatility Penalty**: 1 + ATR / Closing Price  
- **Normalized Pearl Score**: scaled to 0–100

### 5. ⭐ Star Ratings
- ≥ 81 → ★★★★★  
- ≥ 61 → ★★★★☆  
- ≥ 41 → ★★★☆☆  
- ≥ 21 → ★★☆☆☆  
- > 0 → ★☆☆☆☆  
- = 0 → ☆☆☆☆☆  

---

## 🖥️ Dashboard

- Built with **Streamlit**.
- Shows **Top 10 / Bottom 10 pearls**.
- Interactive filters for custom screening.
- Styled tables with arrows and stars.
- Export filtered results as CSV with timestamped filenames.

---



### 🔄 Data Flow Diagram (ASCII fallback)

GitHub Actions Scheduler (17:30 KST weekdays)
        |
        v
   scanner.py
        |
        v
+----------------------+     +------------------------+
| output/latest.csv    | --> | Streamlit Dashboard    |
+----------------------+     |  - Top/Bottom 10       |
        |                   |  - Filters             |
        v                   |  - Exports             |
+----------------------+     +------------------------+
| output/fetch_time.txt|
+----------------------+
            |
            v
   Dashboard shows "Data last fetched ..."
















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
