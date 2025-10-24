import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Binance 4h Volume Explosion Tracker", layout="wide")
st.title("💥 Binance 4h Liquidity Spike Tracker")

BASE_URL = "https://api.binance.com/api/v3"

# ✅ جلب كل أزواج USDT
def get_usdt_symbols():
    url = f"{BASE_URL}/exchangeInfo"
    r = requests.get(url, timeout=10)
    data = r.json()
    symbols = [
        s["symbol"] for s in data["symbols"]
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"
    ]
    return symbols

# ✅ دالة تجيب بيانات آخر 8 ساعات لأي رمز
def get_volume_change(symbol):
    try:
        url = f"{BASE_URL}/klines"
        params = {"symbol": symbol, "interval": "1h", "limit": 8}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if len(data) < 8:
            return None

        vols = [float(candle[5]) for candle in data]  # حجم التداول (volume)
        last4 = sum(vols[-4:])
        prev4 = sum(vols[:4])
        change_pct = ((last4 - prev4) / prev4 * 100) if prev4 != 0 else None

        # السعر الحالي من آخر شمعة
        close_price = float(data[-1][4])

        return {
            "Symbol": symbol,
            "Prev 4h Vol": round(prev4, 2),
            "Last 4h Vol": round(last4, 2),
            "Change %": round(change_pct, 2) if change_pct is not None else None,
            "Price": round(close_price, 6),
            "TPS": "—"  # مؤقتًا لحد ما نربط مصدر الـ TPS
        }
    except Exception:
        return None

# ✅ تحميل البيانات
symbols = get_usdt_symbols()
st.write(f"✅ Found {len(symbols)} USDT pairs on Binance")

rows = []
progress = st.progress(0)

for i, sym in enumerate(symbols):
    info = get_volume_change(sym)
    if info and info["Change %"] is not None:
        rows.append(info)
    progress.progress((i + 1) / len(symbols))
    time.sleep(0.15)  # لتقليل ضغط API

df = pd.DataFrame(rows)
df = df.sort_values("Change %", ascending=False).head(50)  # أعلى 50 عملة

# ✅ تلوين موجب وسالب
def color_pos_neg(val):
    try:
        if val is None:
            return ""
        return "color: green" if val > 0 else "color: red"
    except:
        return ""

st.dataframe(
    df.style.applymap(color_pos_neg, subset=["Change %"]),
    use_container_width=True
        )
