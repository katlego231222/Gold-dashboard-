import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GOLD SNIPER LIVE", page_icon="🎯", layout="wide")
if "signals" not in st.session_state:
    st.session_state.signals = [
        {"Time": "18:35", "Pair": "GOLD", "Type": "BUY", "Entry": 4285, "SL": 4270, "TP1": 4295, "TP2": 4310, "Result": "TP1 HIT +100 pips 🔥"},
    ]
st.title("🎯 GOLD SNIPER LIVE - Kagiso")
st.markdown("**WhatsApp VIP: 0637247675** | Live from TradingView Alerts")
st.link_button("📲 JOIN VIP WHATSAPP", "https://wa.me/27637247675?text=Hi%20Gold%20Sniper%20-%20VIP%20please")
with st.expander("➕ ADD NEW SIGNAL (Tap here)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pair = st.selectbox("Pair", ["GOLD", "EURUSD", "GBPUSD", "NAS100"])
        entry = st.number_input("Entry Price", value=4300.0)
    with col2:
        type_ = st.selectbox("Type", ["BUY", "SELL"])
        sl = st.number_input("Stop Loss", value=4285.0)
    with col3:
        tp1 = st.number_input("TP1", value=4315.0)
        tp2 = st.number_input("TP2", value=4330.0)
    if st.button("🚀 POST SIGNAL LIVE"):
        new_sig = {"Time": datetime.now().strftime("%H:%M"),"Pair": pair, "Type": type_, "Entry": entry, "SL": sl, "TP1": tp1, "TP2": tp2, "Result": "LIVE 🔴"}
        st.session_state.signals.insert(0, new_sig)
        st.success(f"Posted! {type_} {pair} @ {entry} is now LIVE!")
df = pd.DataFrame(st.session_state.signals)
st.dataframe(df, use_container_width=True, hide_index=True)