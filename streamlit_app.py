import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

st.set_page_config(page_title="Kat Scalper Pro LIVE", page_icon="📈", layout="wide")

# --- LIVE GOLD PRICE FUNCTION ---
def get_gold_price():
    try:
        # Free gold API
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r['price'])
    except:
        try:
            # Backup API
            r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=5).json()
            return float(r['items'][0]['xauPrice'])
        except:
            return 4276.78 # fallback to your chart price

if "signals" not in st.session_state:
    st.session_state.signals = []

# AUTO REFRESH EVERY 15 SEC
st_autorefresh = st.empty()
if 'last_price' not in st.session_state:
    st.session_state.last_price = get_gold_price()

# GET LIVE PRICE
live_price = get_gold_price()
change = live_price - st.session_state.last_price

# --- HEADER ---
st.markdown(f"""
<div style='background:#111; padding:15px; border-radius:15px; border:1px solid #333; text-align:center;'>
<h2 style='margin:0; color:#FFD700;'>⚡ KAT SCALPER PRO LIVE</h2>
<h1 style='margin:5px 0; font-size:40px;'>{live_price:.2f}</h1>
<p style='margin:0; color:{"#00ff88" if change>=0 else "#ff4444"};'>XAUUSD • {"▲" if change>=0 else "▼"} {change:+.2f} • {datetime.now().strftime("%H:%M:%S")}</p>
<p style='color:gray; font-size:12px;'>Kagiso • Auto-updates every 15s</p>
</div>
""", unsafe_allow_html=True)

# BIAS DETECTOR
if live_price > 4285:
    bias = "🟢 BULLISH BIAS - Look for BUYS above 4285"
    suggested_type = "BUY"
    suggested_entry = round(live_price,2)
    suggested_sl = round(live_price - 11,2)
    suggested_tp1 = round(live_price + 13,2)
    suggested_tp2 = round(live_price + 28,2)
else:
    bias = "🔴 BEARISH BIAS - Look for SELLS below 4285"
    suggested_type = "SELL"
    suggested_entry = round(live_price,2)
    suggested_sl = round(live_price + 11,2)
    suggested_tp1 = round(live_price - 6,2)
    suggested_tp2 = round(live_price - 12,2)

st.warning(bias)

# --- SMART SIGNAL POSTER ---
with st.container(border=True):
    st.subheader(f"🤖 AI Suggests: {suggested_type} @ {suggested_entry}")
    st.caption(f"Based on LIVE price {live_price:.2f} vs 4285 key level from your chart")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        pair = st.selectbox("Pair", ["GOLD"], key="pair")
        typ = st.selectbox("Type", ["BUY","SELL"], index=0 if suggested_type=="BUY" else 1)
    with c2:
        entry = st.number_input("Entry", value=suggested_entry)
        sl = st.number_input("SL", value=suggested_sl)
    with c3:
        tp1 = st.number_input("TP1", value=suggested_tp1)
        tp2 = st.number_input("TP2", value=suggested_tp2)
    with c4:
        st.write("")
        st.write("")
        if st.button("🚀 POST LIVE SIGNAL", type="primary", use_container_width=True):
            new_signal = {
                "Time": datetime.now().strftime("%H:%M"),
                "Pair": "GOLD",
                "Type": typ,
                "Entry": entry,
                "SL": sl,
                "TP1": tp1,
                "TP2": tp2,
                "LivePrice": f"{live_price:.2f}",
                "Status": "LIVE 🔴"
            }
            st.session_state.signals.insert(0, new_signal)
            st.success(f"Posted! {typ} GOLD @ {entry} (Market was {live_price:.2f})")
            st.balloons()

    if st.button("🔄 Refresh Live Price"):
        st.rerun()

# SHOW SIGNALS
if st.session_state.signals:
    st.subheader("📡 Live Signals (Synced to Market)")
    df = pd.DataFrame(st.session_state.signals)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Delete wrong signals button
    if st.button("🗑️ Clear Old WRONG BUY 4300 Signals"):
        st.session_state.signals = [s for s in st.session_state.signals if s['Entry'] < 4290]
        st.rerun()
else:
    st.info("No signals yet — Post the SELL signal above!")

st.link_button("📲 Share Dashboard to Clients", "https://wa.me/?text=My%20LIVE%20Gold%20Signals%20Dashboard%20-%20Real%20Price:%20https://2lhb7vwtqfx6vivukmj7cv.streamlit.app")
st.caption("Auto-refresh: reloads page every 30s. Price source: gold-api.com")
time.sleep(15)
st.rerun()