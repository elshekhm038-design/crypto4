import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Crypto Liquidity Monitor", layout="wide")

st.title("💧 Crypto Liquidity Monitor (Top 20)")
st.caption("Source: Binance API — Updated manually")

def get_data():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    data = requests.get(url).json()

    coins = []
    for d in data:
        if isinstance(d.get('symbol'), str) and d['symbol'].endswith('USDT'):
            vol = float(d['quoteVolume'])
            chg = abs(float(d['priceChangePercent']))
            bid = float(d['bidPrice'])
            ask = float(d['askPrice'])
            spread = (ask - bid) / bid if bid else 0
            if spread > 0:
                liquidity = (vol * chg) / spread
                coins.append([
                    d['symbol'],
                    round(vol / 1_000_000, 2),
                    round(chg, 2),
                    round(spread * 100, 4),
                    round(liquidity / 1_000_000, 2)
                ])

    df = pd.DataFrame(coins, columns=["Symbol", "Volume (M USDT)", "Change %", "Spread %", "Liquidity Score"])
    df = df.sort_values(by="Liquidity Score", ascending=False).head(20)
    return df

if st.button("🔄 Update Data"):
    df = get_data()
    st.success("Data updated successfully!")
    st.dataframe(df.style.background_gradient(cmap="YlGnBu", subset=["Liquidity Score", "Change %", "Volume (M USDT)"]))
else:
    st.info("Click 'Update Data' to fetch the latest information.")
