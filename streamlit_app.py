import streamlit as st, pandas as pd, requests
import plotly.graph_objects as go
st.set_page_config(layout="wide")
def get_btc():
 try:
  u="https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
  r=requests.get(u,timeout=10).json()
  prices=r['prices']
  df=pd.DataFrame(prices,columns=['t','C'])
  df['O']=df['C']; df['H']=df['C']; df['L']=df['C']
  return float(df['C'].iloc[-1]),df
 except:
  return 108500,None
def get_gold():
 try:
  return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
 except:
  return 4286
g=get_gold()
b,d=get_btc()
st.title("Kat Scalper Pro 24/7")
st.write(f"GOLD ${g} | BTC ${b:.0f}")
if d is not None:
 d['E50']=d['C'].ewm(50).mean()
 st.metric("BTC",f"${b:.0f}")
 fig=go.Figure()
 fig.add_trace(go.Scatter(y=d['C'],name="BTC"))
 fig.update_layout(height=300)
 st.plotly_chart(fig,use_container_width=True)
else:
 st.write("Loading BTC...")
st.success("App Working!")