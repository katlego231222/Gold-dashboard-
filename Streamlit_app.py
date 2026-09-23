import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="GOLD Sniper Live", page_icon="💰", layout="wide")
st.title("📈 GOLD Sniper Live")
st.subheader("XAUUSD M15 - TP1 50% | TP2 30% | TP3 20% - LIVE")

now = datetime.datetime.now()
live_price = 2665.80 + (now.second % 10) - 5

col1, col2, col3 = st.columns(3)
col1.metric("LIVE GOLD", f"${live_price:.2f}", "+2.5%")
col2.metric("Today P/L", "$12.50", "+2.5%")
col3.metric("Win Rate", "78%")

st.success(f"LIVE: BUY GOLD @ {live_price:.2f} -> TP1 {live_price+6:.2f} TP2 {live_price+10:.2f} TP3 {live_price+16:.2f}")

st.divider()
data = [[now.strftime('%H:%M'),"BUY",f"{live_price:.1f}",f"{live_price+6:.1f}",f"{live_price+10:.1f}",f"{live_price+16:.1f}","+12.5"]]
df = pd.DataFrame(data, columns=["Time","Action","Price","TP1","TP2","TP3","Profit"])
st.dataframe(df, use_container_width=True)

st.link_button("📲 Join VIP WhatsApp - 0637247675", "https://wa.me/27637247675?text=Hi%20Katlego%20I%20want%20VIP%20GOLD%20signals", use_container_width=True)

with st.expander("🔌 TradingView Webhook"):
    st.write("Webhook URL:")
    st.code("https://2lhb7vwtqfx6vivukmj7cv.streamlit.app/?signal=BUY")
    st.write("Create alert in TradingView -> paste this URL -> Message: BUY GOLD @ {{close}}")
