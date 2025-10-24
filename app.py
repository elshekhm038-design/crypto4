import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Crypto Liquidity Monitor", layout="wide")

st.title("💧 Top 20 Most Liquid Cryptos (CoinGecko Source)")

def get_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "volume_desc", "per_page": 20, "page": 1}
    try:
        data = requests.get(url, params=params).json()
        coins = []
        for d in data:
            coins.append([
                d["symbol"].upper(),
                d["name"],
                round(d["current_price"], 4),
                round(d["total_volume"] / 1_000_000, 2),
                round(d["price_change_percentage_24h"], 2)
            ])

        df = pd.DataFrame(coins, columns=["Symbol", "Name", "Price (USD)", "Volume (M USD)", "Change 24h (%)"])
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

if st.button("🔄 Update Data"):
    df = get_data()
    if not df.empty:
        st.success("Data updated successfully!")
        st.dataframe(df.style.background_gradient(cmap="YlGnBu", subset=["Volume (M USD)", "Change 24h (%)"]))
    else:
        st.warning("⚠️ No data available right now.")
else:
    st.info("Click 'Update Data' to fetch the latest information.")
