import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Kat Scalper Pro 24/7", page_icon="📈", layout="wide")

@st.cache_data(ttl=60)
def get_btc_fast():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100"
        r = requests.get(url, timeout=10).json()
        df = pd.DataFrame(r, columns=["time","open","high","low","close","vol","ct","qvol","trades","taker_base","taker_quote","ignore"])
        df['Close'] = df['close'].astype(float)
        df['Open'] = df['open'].astype(float)
        df['High'] = df['high'].astype(float)
        df['Low'] = df['low'].astype(float)
        price = float(df['Close'].iloc[-1])
        return price, df
    except:
        return 108500.0, None

def get_gold():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=4).json()
        return float(r['price'])
    except:
        return 4286.20

if "signals" not in st.session_state:
    st.session_state.signals = [
        {"Time":"19:02","Pair":"GOLD","Type":"SELL","Entry":4277,"SL":4288,"TP1":4270.96,"TP2":4264.70,"Source":"MANUAL","Status":"LIVE 🔴"}
    ]

gold_price = get_gold()
btc_price, btc_data =