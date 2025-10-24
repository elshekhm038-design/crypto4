import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Binance 4h Volume Explosion Tracker", layout="wide")
st.title("💥 Binance 4h Liquidity Spike Tracker")

BASE_URL = "https://api.binance.com/api/v3"

# ✅ إعداد هيدر عشان Binance ما يعتبركش بوت
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ✅ دالة لجلب كل أزواج USDT مع معالجة الأخطاء
def get_usdt_symbols():
    url = f"{BASE_URL}/exchangeInfo"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()

        # لو الـ response فيه Error
        if "symbols" not in data:
            st.error("❌ Binance API error — حاول بعد دقيقة أو قلل عدد الطلبات")
            st.write("Response:", data)
            st.stop()

        symbols = [
            s["symbol"] for s in data["symbols"]
            if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"
        ]
        return symbols

    except Exception as e:
        st.error(f"⚠️ Network error while getting symbols: {e}")
        st.stop()

# ✅ دالة تجيب بيانات آخر 8 ساعات لأي رمز
def get_volume_change(symbol):
    try:
        url = f"{BASE_URL}/klines"
        params = {"symbol": symbol, "interval": "1h", "limit": 8}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()

        # لو Binance رجّع Error code
        if isinstance(data, dict) and "code" in data:
            return None

        if len(data) < 8:
            return None

        vols = [float(candle[5]) for candle in data]  # حجم التداول
        last4 = sum(vols[-4:])
        prev4 = sum(vols[:4])
        change_pct = ((last4 - prev4) / prev4 * 100) if prev4 != 0 else None
        close_price = float(data[-1][4])  # آخر سعر إغلاق

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
st.info("⏳ Fetching Binance trading pairs...")
symbols = get_usdt_symbols()
st.success(f"✅ Found {len(symbols)} USDT pairs on Binance")

rows = []
progress = st.progress(0)
errors = 0

for i, sym in enumerate(symbols):
    info = get_volume_change(sym)
    if info and info["Change %"] is not None:
        rows.append(info)
    else:
        errors += 1

    progress.progress((i + 1) / len(symbols))
    time.sleep(0.15)  # تخفيف الضغط على Binance API

st.write(f"⚙️ Completed with {errors} skipped symbols.")

# ✅ معالجة البيانات
df = pd.DataFrame(rows)
if df.empty:
    st.error("🚫 No valid data received. Try again later.")
    st.stop()

df = df.sort_values("Change %", ascending=False).head(50)  # أعلى 50 عملة

# ✅ تلوين موجب وسالب
def color_pos_neg(val):
    try:
        if val is None:
            return ""
        return "color: green" if val > 0 else "color: red"
    except:
        return ""

# ✅ عرض النتائج
st.subheader("🔥 Top 50 Coins by 4h Volume Spike")
st.dataframe(
    df.style.applymap(color_pos_neg, subset=["Change %"]),
    use_container_width=True
        )
