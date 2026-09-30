import streamlit as st, requests, pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go
try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=7000, key="buy_sell_label")
except: pass

st.set_page_config(layout="centered", page_title="BUY SELL LABEL", page_icon="🏦")
if 'last_entry' not in st.session_state: st.session_state.last_entry=0
if 'tp1_hit' not in st.session_state: st.session_state.tp1_hit=False
if 'be_active' not in st.session_state: st.session_state.be_active=False

def get_price():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
 except: return 4153.90

def get_klines(interval, limit=200):
 try:
  data=requests.get(f"https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval={interval}&limit={limit}",timeout=5).json()
  if isinstance(data,list) and len(data)>20:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k])
   return df
 except: pass
 base=get_price()
 return pd.DataFrame({'o':[base]*limit,'h':[base*1.001]*limit,'l':[base*0.999]*limit,'c':[base]*limit})

live=get_price()
df=get_klines("15m"); df_c=df.iloc[:-1]

# BANK S&D
demands=[]; supplies=[]
for i in range(20, len(df_c)-3):
 body=df_c['c'].iloc[i]-df_c['o'].iloc[i]
 rng=df_c['h'].iloc[i-8:i].max() - df_c['l'].iloc[i-8:i].min()
 if body > rng*0.6: demands.append({"mid":float(df_c['l'].iloc[i-1]+df_c['l'].iloc[i])/2,"sl":float(df_c['l'].iloc[i-1])})
 if body < -rng*0.6: supplies.append({"mid":float(df_c['h'].iloc[i]+df_c['h'].iloc[i-1])/2,"sl":float(df_c['h'].iloc[i-1])})

df['e9']=df['c'].ewm(9).mean(); df['e21']=df['c'].ewm(21).mean()
e9=float(df['e9'].iloc[-1]); e21=float(df['e21'].iloc[-1])

if demands and e9>e21: sig="BUY"; z=demands[-1]; entry=z['mid']; sl_orig=z['sl']-0.8
else: sig="SELL"; z=supplies[-1] if supplies else {"mid":live+2,"sl":live+3}; entry=z['mid']; sl_orig=z['sl']+0.8

if sig=="BUY": tp1=entry+5; tp2=entry+10; tp3=entry+20; hit=live>=tp1
else: tp1=entry-5; tp2=entry-10; tp3=entry-20; hit=live<=tp1

if hit: st.session_state.be_active=True; st.session_state.tp1_hit=True
sl = entry if st.session_state.be_active else sl_orig

# --- ONLY BUY / SELL LABEL BIG ---
if sig=="BUY":
 st.markdown(f"<h1 style='text-align:center;background:#00ff88;color:#000;padding:20px;border-radius:15px;font-size:50px;margin:0'>🟢 BUY</h1>", unsafe_allow_html=True)
else:
 st.markdown(f"<h1 style='text-align:center;background:#ff4444;color:#fff;padding:20px;border-radius:15px;font-size:50px;margin:0'>🔴 SELL</h1>", unsafe_allow_html=True)

st.markdown(f"<h3 style='text-align:center'>LIVE ${live:.2f} | ENTRY ${entry:.2f} | { '🔒 BE SAFE' if st.session_state.be_active else 'LIVE' }</h3>", unsafe_allow_html=True)

# Chart
fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_c))), open=df_c['o'], high=df_c['h'], low=df_c['l'], close=df_c['c']))
fig.add_hline(y=entry, line_color="yellow", line_width=4, annotation_text=f"ENTRY {entry:.2f} {sig}")
fig.add_hline(y=sl, line_color="blue" if st.session_state.be_active else "red", line_width=3)
fig.add_hline(y=tp1, line_color="#00ff88", line_width=2, line_dash="dot")
fig.add_hline(y=tp2, line_color="#00ff88", line_width=2, line_dash="dash")
fig.add_hline(y=tp3, line_color="#00ff88", line_width=3)
fig.add_hline(y=live, line_color="white", line_dash="dot")
fig.update_layout(height=500, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

c1,c2=st.columns(2)
c1.metric("ENTRY", f"${entry:.2f}")
c2.metric("LIVE", f"${live:.2f}", sig)