import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os
from pykrx.stock import get_market_cap_by_date

# -------------------------------
# Config
# -------------------------------
today = datetime.today()
OUTPUT_FILE = f"output/kospi_kosdaq_technical_{today.strftime('%Y%m%d')}.csv"

print("Fetching KRX listings...")
krx = fdr.StockListing('KRX')[['Code','Name','Market']]

# Filter for KOSPI + KOSDAQ
kospi = krx[krx['Market'] == 'KOSPI']
kosdaq = krx[krx['Market'] == 'KOSDAQ']
stock_list = pd.concat([kospi, kosdaq]).drop_duplicates(subset=['Code']).reset_index(drop=True)

# ✅ Test mode: limit to 10 tickers
stock_list = stock_list.head(10)

os.makedirs("output", exist_ok=True)

# -------------------------------
# Helper: find last trading day
# -------------------------------
def get_last_trading_day(code):
    """Return the last trading day string (YYYYMMDD) for a given stock code."""
    # Use PyKRX to get recent market cap data (last 10 days)
    end = today.strftime("%Y%m%d")
    start = (today - timedelta(days=10)).strftime("%Y%m%d")
    cap_df = get_market_cap_by_date(start, end, code)
    if cap_df.empty:
        return None
    return cap_df.index[-1].strftime("%Y%m%d")

# -------------------------------
# Technical Indicators
# -------------------------------
def compute_indicators(df):
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma60 = df['Close'].rolling(60).mean().iloc[-1]

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain.iloc[-1] / avg_loss.iloc[-1] if avg_loss.iloc[-1] != 0 else np.nan
    rsi = 100 - (100 / (1 + rs)) if rs == rs else np.nan

    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_val = macd.iloc[-1]
    macd_signal_val = macd_signal.iloc[-1]

    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]

    obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum().iloc[-1]

    return ma20, ma60, rsi, macd_val, macd_signal_val, atr, obv

# -------------------------------
# Main loop
# -------------------------------
results = []

print(f"Fetching technical + fundamental data for {len(stock_list)} stocks...")
for i, stock in enumerate(stock_list.itertuples(), start=1):
    code = stock.Code
    name = stock.Name

    try:
        # ✅ Get MarketCap from PyKRX using last trading day
        try:
            last_day = get_last_trading_day(code)
            if last_day:
                cap_df = get_market_cap_by_date(last_day, last_day, code)
                market_cap = cap_df['시가총액'].iloc[0] if not cap_df.empty else None
            else:
                market_cap = None
        except Exception:
            market_cap = None

        # ✅ Get OHLCV data from FinanceDataReader
        df = fdr.DataReader(code)
        if df.empty:
            continue

        closing_price = float(df['Close'].iloc[-1])
        daily_volume = int(df['Volume'].iloc[-1])
        avg_volume = df['Volume'].rolling(20).mean().iloc[-1]

        if daily_volume == 0 or pd.isna(avg_volume) or avg_volume == 0:
            volume_spike = np.nan
            data_status = "Data Missing"
        else:
            volume_spike = round(daily_volume / avg_volume, 2)
            data_status = "OK"

        ma5 = df['Close'].rolling(5).mean().iloc[-1]
        diff = closing_price - ma5
        tolerance = closing_price * 0.002

        if abs(diff) <= tolerance:
            trend_arrow = "→"
        elif diff > 0:
            trend_arrow = "↑"
        else:
            trend_arrow = "↓"

        ma20, ma60, rsi, macd_val, macd_signal_val, atr, obv = compute_indicators(df)

        if pd.notna(volume_spike):
            bullish_signals = 0
            if closing_price > ma20:
                bullish_signals += 1
            if closing_price > ma60:
                bullish_signals += 1
            if macd_val > macd_signal_val:
                bullish_signals += 1
            trend_strength = 1 + 0.2 * bullish_signals

            momentum_quality = 1 - abs(rsi - 50) / 50 if rsi == rsi else 1.0
            momentum_quality = max(momentum_quality, 0)

            volatility_penalty = 1 + (atr / closing_price if closing_price > 0 else 0)

            pearl_score = (volume_spike * trend_strength * momentum_quality) / volatility_penalty
            pearl_score = float(round(pearl_score, 2))

            pearl_score_norm = min(max(pearl_score / 2.0 * 100, 0), 100)
            pearl_score_norm = float(round(pearl_score_norm, 1))

            if pearl_score_norm >= 81:
                stars = "★★★★★"
            elif pearl_score_norm >= 61:
                stars = "★★★★☆"
            elif pearl_score_norm >= 41:
                stars = "★★★☆☆"
            elif pearl_score_norm >= 21:
                stars = "★★☆☆☆"
            elif pearl_score_norm > 0:
                stars = "★☆☆☆☆"
            else:
                stars = "☆☆☆☆☆"
        else:
            pearl_score = None
            pearl_score_norm = None
            stars = "☆☆☆☆☆"

        results.append({
            "StockCode": code,
            "StockName_KR": name,
            "MarketCap": market_cap,  # ✅ raw number from PyKRX
            "ClosingPrice": closing_price,
            "DailyVolume": daily_volume,
            "VolumeSpike": volume_spike,
            "TrendArrow": trend_arrow,
            "MA20": float(round(ma20, 2)) if ma20 == ma20 else None,
            "MA60": float(round(ma60, 2)) if ma60 == ma60 else None,
            "RSI(14)": float(round(rsi, 2)) if rsi == rsi else None,
            "MACD": float(round(macd_val, 2)) if macd_val == macd_val else None,
            "MACD_Signal": float(round(macd_signal_val, 2)) if macd_signal_val == macd_signal_val else None,
            "Volatility(ATR)": float(round(atr, 2)) if atr == atr else None,
            "OBV": int(obv) if obv == obv else None,
            "PearlScore": pearl_score,
            "PearlScore_Normalized": pearl_score_norm,
            "PearlScore_Stars": stars,
            "PearlScore_Status": data_status
        })

    except Exception as e:
        print(f"Error with {code}: {e}")

    time.sleep(0.5)
    print(f"Processed {i} / {len(stock_list)} stocks...")

# -------------------------------
# Save results
# -------------------------------
df_out = pd.DataFrame(results)
df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"✅ Scanner finished. Output saved to {OUTPUT_FILE}")
