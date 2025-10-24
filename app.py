import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Crypto Liquidity Monitor", layout="wide")
st.title("💧 Top 20 Cryptos | 4H Inflow, 4H Change & TPS")

def get_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "volume_desc", "per_page": 20, "page": 1}
    data = requests.get(url, params=params).json()
    coins = []

    for d in data:
        symbol = d["symbol"].upper()
        coin_id = d["id"]

        # بيانات آخر 4 ساعات
        chart_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        chart_params = {"vs_currency": "usd", "days": 0.2}  # ~4.8 ساعات
        chart = requests.get(chart_url, params=chart_params).json()

        volumes = [v[1] for v in chart.get("total_volumes", [])]
        if len(volumes) >= 2:
            vol_4h = (volumes[-1] - volumes[0]) / 1_000_000  # بالمليون دولار
            vol_4h_change = ((volumes[-1] - volumes[0]) / volumes[0]) * 100
        else:
            vol_4h = 0
            vol_4h_change = 0

        # تقدير بسيط لـ TPS
        tps = round(d["total_volume"] / (d["current_price"] * 86_400), 2)

        coins.append([
            symbol,
            d["name"],
            round(d["current_price"], 4),
            round(d["total_volume"] / 1_000_000, 2),
            round(vol_4h, 2),
            round(vol_4h_change, 2),
            tps,
            round(d["price_change_percentage_24h"], 2)
        ])

        time.sleep(0.4)

    df = pd.DataFrame(coins, columns=[
        "Symbol", "Name", "Price (USD)",
        "24h Volume (M USD)", "4h Inflow (M USD)",
        "4h Volume Change (%)", "TPS", "Change 24h (%)"
    ])

    return df


def color_positive_negative(val):
    """لون أخضر للقيم الموجبة وأحمر للسالبة"""
    if isinstance(val, (int, float)):
        color = 'green' if val > 0 else 'red' if val < 0 else 'white'
        return f'color: {color}'
    return ''

if st.button("🔄 Update Data"):
    df = get_data()
    if not df.empty:
        st.success("✅ Data updated successfully!")

        st.dataframe(
            df.style.applymap(color_positive_negative, subset=["4h Volume Change (%)", "Change 24h (%)"])
        )

    else:
        st.warning("⚠️ No data available right now.")
else:
    st.info("Click 'Update Data' to fetch the latest information.")
