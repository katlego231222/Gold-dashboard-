import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="GOLD Sniper Live", page_icon="📈")

st.title("📈 GOLD Sniper Live")
st.subheader("XAUUSD M15 - TP1 50% | TP2 30% | TP3 20%")

col1, col2, col3 = st.columns(3)
col1.metric("Today", "$12.50", "+2.5%")
col2.metric("Win Rate", "78%")
col3.metric("Signals", "5")

st.success("LIVE: BUY GOLD @ 2645.50 -> TP1 2651.50 TP2 2655.50 TP3 2661.50")

st.divider()
st.write("This dashboard will update automatically from your bot")

# sample table
data = [["17:45","BUY","2645.5","2651.5","2655.5","2661.5","+12.5"]]
df = pd.DataFrame(data, columns=["Time","Action","Price","TP1","TP2","TP3","Profit"])
st.dataframe(df, use_container_width=True)

st.link_button("Join VIP WhatsApp", "https://wa.me/277XXXXXXXX")
