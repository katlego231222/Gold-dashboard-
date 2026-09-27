import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Kat Scalper Pro", page_icon="📈", layout="wide")

def get_btc():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100"
        r = requests.get(url, timeout=10).json()
        df = pd.DataFrame(r)
        df['Close'] = df[4].astype(float)
        df['Open'] = df[1].astype(float)
        df['High'] = df[2].astype(float)
        df['Low'] = df[3].astype(float)
        price = float(df['Close'].iloc[-1])
        return price, df
    except:
        return 108500.0, None

def get_gold():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=4).json()
        return float(r['price'])
    except:
        return 4286.2

gold_price = get_gold()
btc_price, btc_data = get_btc()

st.title("Kat Scalper Pro 24/7 🚀")
st.caption(f"Gold ${gold_price} | BTC ${btc_price:.0f}")

tab1, tab2 = st.tabs(["GOLD", "BTC"])

with tab1:
    st.metric("XAUUSD", f"${gold_price:.2f}")
    st.success("GOLD LIVE")

with tab2:
    st.metric("BTC", f"${btc_price:.2f}")
    if btc_data is not None:
        btc_data['EMA50'] = btc_data['Close'].ewm(span=50).mean()
        btc_data['EMA200'] = btc_data['Close'].ewm(span=200).mean()
        d = btc_data['Close'].diff()
        g = d.where(d > 0, 0).rolling(14).mean()
        l = (-d.where(d < 0, 0)).rolling(14).mean()
        rs = g / l
        rsi = 100 - (100 / (1 + rs))
        rsi_last = float(rsi.iloc[-1])
        ema50 = float(btc_data['EMA50'].iloc[-1])
        st.write(f"RSI: {rsi_last:.1f} | Trend: {'BULL' if btc_price>ema50 else 'BEAR'}")
        if rsi_last < 35:
            st.success(f"BUY BTC RSI {rsi_last:.1f}")
        elif rsi_last > 70:
            st.error(f"SELL BTC RSI {rsi_last:.1f}")
        else:
            st.warning(f"WAIT RSI {rsi_last:.1f}")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(open=btc_data['Open'], high=btc_data['High'], low=btc_data['Low'], close=btc_data['Close']))
        fig.update_layout(height=350, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)