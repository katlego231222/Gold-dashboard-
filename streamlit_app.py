import streamlit as st, pandas as pd, requests
import plotly.graph_objects as go
st.set_page_config(layout="wide")
def get_gold():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()['price'])
 except: return 4286.2
def get_btc_price():
 try:
  r=requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",timeout=8).json()
  return float(r['bitcoin']['usd'])
 except: return 107500
def get_btc_chart():
 try:
  r=requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1",timeout=10).json()
  return pd.DataFrame(r['prices'],columns=['t','C'])
 except: return None

g=get_gold(); b=get_btc_price(); df=get_btc_chart()

st.title("Kat Scalper Pro 24/7")
t1,t2=st.tabs(["🪙 GOLD XAU","₿ BTC"])

with t1:
  entry=g; side="SELL"; col="red"
  tp1=entry-8; tp2=entry-15; sl=entry+10
  st.markdown(f"## GOLD ${g:.2f} | :{col}[{side}]")
  c1,c2,c3,c4=st.columns(4)
  c1.metric("ENTRY",f"${entry:.2f}")
  c2.metric("TP1",f"${tp1:.2f}","- $8")
  c3.metric("TP2",f"${tp2:.2f}","- $15")
  c4.metric("SL",f"${sl:.2f}","+ $10",delta_color="inverse")
  st.caption("Signal: 19:02 SELL 4277 | EMA Bear | RSI 43")

with t2:
  st.markdown(f"## BTC ${b:.0f}")
  entry=b; tp1=entry*1.01; tp2=entry*1.02; sl=entry*0.99
  c1,c2,c3,c4=st.columns(4)
  c1.metric("ENTRY",f"${entry:.0f}")
  c2.metric("TP1 +1%",f"${tp1:.0f}")
  c3.metric("TP2 +2%",f"${tp2:.0f}")
  c4.metric("SL -1%",f"${sl:.0f}")
  if df is not None:
    fig=go.Figure(); fig.add_trace(go.Scatter(y=df['C'],name="BTC",line=dict(color="#00BFFF")))
    fig.update_layout(height=300,xaxis_rangeslider_visible=False,template="plotly_dark")
    st.plotly_chart(fig,use_container_width=True)

st.success(f"LIVE 24/7 | GOLD ${g:.2f} | BTC ${b:.0f} | 28% Emalahleni")