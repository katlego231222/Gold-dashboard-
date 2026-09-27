import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Kat Scalper Pro 24/7", page_icon="📈", layout="wide")

# --- LIVE GOLD PRICE ---
def get_gold():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=4).json()
        return float(r['price'])
    except:
        return 4276.52

def get_btc():
    try:
        b = yf.download("BTC-USD", period="1d", interval="5m", progress=False)
        return float(b['Close'].iloc[-1]), b
    except:
        return 108500.0, None

if "signals" not in st.session_state:
    st.session_state.signals = [
        {"Time":"19:02","Pair":"GOLD","Type":"SELL","Entry":4277,"SL":4288,"TP1":4270.96,"TP2":4264.70,"Source":"MANUAL","Status":"LIVE 🔴"}
    ]

# --- WEBHOOK RECEIVER ---
params = st.query_params
if "entry" in params:
    try:
        entry = float(params.get("entry", 4277))
        typ = params.get("type", "SELL")
        sl = float(params.get("sl", 4288))
        tp1 = float(params.get("tp1", 4270))
        tp2 = float(params.get("tp2", 4264))
        new_sig = {"Time": datetime.now().strftime("%H:%M"), "Pair":"GOLD", "Type":typ, "Entry":entry, "SL":sl, "TP1":tp1, "TP2":tp2, "Source":"WEBHOOK", "Status":"LIVE 🔴"}
        if not any(s['Entry']==entry and s['Type']==typ for s in st.session_state.signals):
            st.session_state.signals.insert(0, new_sig)
    except: pass

gold_price = get_gold()
btc_price, btc_data = get_btc()

st.title("Kat Scalper Pro 24/7 🚀")
st.caption(f"Live Gold: ${gold_price} | BTC: ${btc_price:,.0f} | Emalahleni SA")

tab_gold, tab_btc = st.tabs(["🥇 GOLD Signals", "₿ BTC Indicator"])

with tab_gold:
    st.metric("XAUUSD", f"${gold_price:.2f}")
    st.dataframe(pd.DataFrame(st.session_state.signals), use_container_width=True)
    st.success(f"NOW: GOLD @ {gold_price} | If price > 4297 → SELL, If < 4276 → BUY bounce to 4290 (you made R419 here!)")

with tab_btc:
    st.subheader("₿ BTC Live Indicator — For Streamlit")
    if btc_data is not None and len(btc_data) > 20:
        btc_data['EMA50'] = btc_data['Close'].ewm(span=50).mean()
        btc_data['EMA200'] = btc_data['Close'].ewm(span=200).mean()
        delta = btc_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        btc_data['RSI'] = 100 - (100 / (1 + rs))
        btc_data['MACD'] = btc_data['Close'].ewm(12).mean() - btc_data['Close'].ewm(26).mean()
        btc_data['Signal'] = btc_data['MACD'].ewm(9).mean()

        rsi = float(btc_data['RSI'].iloc[-1])
        ema50 = float(btc_data['EMA50'].iloc[-1])
        macd = float(btc_data['MACD'].iloc[-1])
        sig = float(btc_data['Signal'].iloc[-1])

        col1, col2, col3 = st.columns(3)
        col1.metric("BTC Price", f"${btc_price:,.2f}")
        col2.metric("RSI (14)", f"{rsi:.1f}")
        col3.metric("Trend", "BULLISH" if btc_price > ema50 else "BEARISH")

        if rsi < 35 and macd > sig:
            st.success(f"🟢 BUY BTC @ ${btc_price:,.0f} | SL ${btc_price*0.98:,.0f} | TP ${btc_price*1.03:,.0f} | RSI {rsi:.1f} OVERSOLD")
        elif rsi > 70:
            st.error(f"🔴 SELL BTC @ ${btc_price:,.0f} | SL ${btc_price*1.02:,.0f} | TP ${btc_price*0.97:,.0f} | RSI {rsi:.1f} OVERBOUGHT")
        else:
            st.warning(f"⚪ WAIT BTC | RSI {rsi:.1f} | EMA50 ${ema50:,.0f} | MACD {'BUY' if macd>sig else 'SELL'}")

        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=btc_data.index, open=btc_data['Open'], high=btc_data['High'], low=btc_data['Low'], close=btc_data['Close'], name="BTC"))
        fig.add_trace(go.Scatter(x=btc_data.index, y=btc_data['EMA50'], line=dict(color='blue', width=1), name="EMA50"))
        fig.add_trace(go.Scatter(x=btc_data.index, y=btc_data['EMA200'], line=dict(color='red', width=1), name="EMA200"))
        fig.update_layout(height=400, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Loading BTC data...")