import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="Kat Scalper Pro 24/7", page_icon="🤖", layout="wide")

# --- LIVE GOLD PRICE ---
def get_gold():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=4).json()
        return float(r['price'])
    except:
        return 4276.52

if "signals" not in st.session_state:
    st.session_state.signals = [
        {"Time":"19:02","Pair":"GOLD","Type":"SELL","Entry":4277,"SL":4288,"TP1":4270.96,"TP2":4264.70,"Source":"MANUAL","Status":"LIVE 🔴"}
    ]

# --- WEBHOOK RECEIVER (TRADINGVIEW) ---
# TradingView will call: yourapp.streamlit.app/?entry=4277&type=SELL&sl=4288&tp1=4270&tp2=4264
params = st.query_params
if "entry" in params:
    try:
        entry = float(params.get("entry", 4277))
        typ = params.get("type", "SELL")
        sl = float(params.get("sl", 4288))
        tp1 = float(params.get("tp1", 4270))
        tp2 = float(params.get("tp2", 4264))
        
        # Avoid duplicate
        if not any(abs(s['Entry']-entry)<1 for s in st.session_state.signals):
            new = {
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Pair": "GOLD",
                "Type": typ,
                "Entry": entry,
                "SL": sl,
                "TP1": tp1,
                "TP2": tp2,
                "Source": "TRADINGVIEW AUTO 🤖",
                "Status": "LIVE 🔴"
            }
            st.session_state.signals.insert(0, new)
            st.success(f"🤖 AUTO SIGNAL RECEIVED FROM TRADINGVIEW: {typ} @ {entry}")
            st.balloons()
    except:
        pass

live = get_gold()
bias = "🔴 BEARISH - SELL below 4285.74" if live < 4285.74 else "🟢 BULLISH - BUY above 4285.74"

st.markdown(f"""
<div style='background:linear-gradient(135deg,#111,#222); padding:20px; border-radius:15px; text-align:center; border:2px solid #FFD700;'>
<h2 style='color:#FFD700; margin:0;'>KAT SCALPER PRO 24/7</h2>
<h1 style='margin:5px; font-size:45px;'>{live:.2f}</h1>
<p style='color:#aaa;'>XAUUSD LIVE • {bias}</p>
<p style='color:#00ff88; font-size:12px;'>● WEBHOOK ACTIVE - Ready for TradingView</p>
</div>
""", unsafe_allow_html=True)

st.info(f"Webhook URL for TradingView: `{st.request.url if hasattr(st,'request') else 'https://2lhb7vwtqfx6vivukmj7cv.streamlit.app'}?entry=4277&type=SELL&sl=4288&tp1=4270&tp2=4264`")

# Manual poster (backup)
with st.expander("➕ Manual Post (if needed)"):
    c1,c2,c3 = st.columns(3)
    with c1:
        typ = st.selectbox("Type", ["SELL","BUY"])
        entry = st.number_input("Entry", value=live)
    with c2:
        sl = st.number_input("SL", value=live+11 if typ=="SELL" else live-11)
        tp1 = st.number_input("TP1", value=4270.96)
    with c3:
        tp2 = st.number_input("TP2", value=4264.70)
        if st.button("POST", type="primary", use_container_width=True):
            st.session_state.signals.insert(0, {"Time":datetime.now().strftime("%H:%M"),"Pair":"GOLD","Type":typ,"Entry":entry,"SL":sl,"TP1":tp1,"TP2":tp2,"Source":"MANUAL","Status":"LIVE"})
            st.rerun()

st.dataframe(pd.DataFrame(st.session_state.signals), use_container_width=True, hide_index=True)

if st.button("🗑️ Clear old BUY 4300"):
    st.session_state.signals = [s for s in st.session_state.signals if s['Entry'] != 4300]
    st.rerun()

st.link_button("📲 Share LIVE Dashboard", "https://wa.me/?text=LIVE%20Gold%20Signals%2024/7:%20https://2lhb7vwtqfx6vivukmj7cv.streamlit.app")

st.caption("After setup, this reads market 24/5 via webhook. Weekend closed.")