import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Crypto Inflow (4h) - CryptoCompare", layout="wide")
st.title("Top 30 by 4h Inflow (CryptoCompare)")

API_KEY = st.secrets["CRYPTOCOMPARE_API_KEY"]  # ضع المفتاح في Streamlit Secrets

headers = {
    "Apikey": API_KEY
}

# مثال دالة تجيب بيانات histohour لحاجة واحدة (pair)
def get_4h_inflow_for_symbol(fsym="BTC", tsym="USD"):
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    # نطلب 8 ساعات (نقدر نحسب آخر 4 ساعات + الـ4 ساعات السابقة)
    params = {
        "fsym": fsym,
        "tsym": tsym,
        "limit": 7,   # سيعيد 8 نقاط زمنية (0..7) -> نستخدم آخر 8 ساعات
        "aggregate": 1
    }
    r = requests.get(url, params=params, headers=headers, timeout=10)
    data = r.json()
    bars = data.get("Data", {}).get("Data", [])
    if len(bars) < 8:
        return None  # بيانات غير كافية
    # volumeto = حجم بالعملة المقابلة (USD مثلاً) لكل ساعة
    vols = [bar.get("volumeto", 0) for bar in bars]
    last4 = sum(vols[-4:])        # آخر 4 ساعات
    prev4 = sum(vols[-8:-4])      # الأربع ساعات اللي قبلهم
    # حساب التغير % (حماية من القسمة على صفر)
    vol_change_pct = ((last4 - prev4) / prev4 * 100) if prev4 else None
    return {
        "fsym": fsym,
        "tsym": tsym,
        "4h_inflow": last4,
        "4h_prev": prev4,
        "4h_change_pct": vol_change_pct
    }

# مثال بسيط: استخدم قائمة رموز (يمكن تعديلها أو سحب قائمة ديناميكية لاحقاً)
symbols = ["BTC","ETH","SOL","BNB","XRP","ADA","DOGE","DOT","LINK","LTC","TRX","MATIC","AVAX","FTM","NEAR","ATOM","BCH","XLM","ALGO","ICP","SAND","AXS","AAVE","MKR","ZEC","EGLD","MANA","GRT","SHIB","FTT"]

rows = []
for s in symbols:
    try:
        info = get_4h_inflow_for_symbol(fsym=s, tsym="USD")
        if info:
            rows.append({
                "Symbol": s,
                "4h Inflow (USD)": round(info["4h_inflow"], 2),
                "4h Change %": round(info["4h_change_pct"], 2) if info["4h_change_pct"] is not None else None
            })
        time.sleep(0.25)  # تخفيف النداءات (rate limit)
    except Exception as e:
        continue

df = pd.DataFrame(rows)
df = df.sort_values("4h Inflow (USD)", ascending=False).head(30)

# تلوين بسيط: أخضر للموجب، أحمر للسالب
def color_pos_neg(val):
    if val is None: return ""
    try:
        return "color: green" if val > 0 else "color: red" if val < 0 else ""
    except:
        return ""

if not df.empty:
    st.dataframe(df.style.applymap(color_pos_neg, subset=["4h Change %"]), use_container_width=True)
else:
    st.warning("No data — تأكد من صلاحية API key أو جرّب لاحقًا.")
