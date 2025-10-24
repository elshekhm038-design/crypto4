import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Binance 4h Inflow Tracker", layout="wide")
st.title("📊 Binance Top Coins by 4h Inflow Surge")

BINANCE_API = "https://api.binance.com/api/v3/exchangeInfo"

# 🟢 جلب كل الأزواج اللي فيها USDT
@st.cache_data(ttl=3600)
def get_usdt_symbols():
    r = requests.get(BINANCE_API, timeout=10)
    data = r.json()
    symbols = []
    for s in data.get("symbols", []):
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING":
            symbols.append(s["symbol"])
    return symbols

# 🟢 دالة تجيب بيانات الـ volume لكل عملة
def get_4h_volume(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": "1h", "limit": 8}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        vols = [float(candle[7]) for candle in data]  # volume بالعملة المقابلة
        last4 = sum(vols[-4:])
        prev4 = sum(vols[-8:-4])
        change_pct = ((last4 - prev4) / prev4 * 100) if prev4 else None
        return last4, prev4, change_pct
    except:
        return None, None, None

# 🟢 (اختياري) TPS Placeholder
# Binance مش بتوفر TPS مباشر، فهنا هنحط placeholder مؤقت لحد ما نربطه بـ API تاني
def get_fake_tps(symbol):
    # رقم عشوائي تقريبي للعرض فقط
    import random
    return round(random.uniform(5, 200), 2)

# تنفيذ
st.info("⏳ Fetching Binance trading pairs...")
symbols = get_usdt_symbols()
st.success(f"✅ Found {len(symbols)} USDT pairs.")

rows = []
progress = st.progress(0)
for i, sym in enumerate(symbols[:80]):  # مبدئيًا نجيب أول 80 عملة لتقليل الضغط
    vol_now, vol_prev, change = get_4h_volume(sym)
    if vol_now:
        rows.append({
            "Symbol": sym,
            "4h Volume": round(vol_now, 2),
            "4h % Change": round(change, 2) if change else None,
            "TPS": get_fake_tps(sym)
        })
    progress.progress((i + 1) / len(symbols[:80]))
    time.sleep(0.2)

df = pd.DataFrame(rows)
if not df.empty:
    df = df.sort_values("4h % Change", ascending=False)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("⚠️ No data fetched. Try again later or check API connection.")
