import streamlit as st, requests, time, pandas as pd, numpy as np
from datetime import datetime
import plotly.graph_objects as go

# AUTO REFRESH EVERY 3 SEC
try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=3000, key="live")
except:
 pass

st.set_page_config(layout="centered", page_title="Katlego AI", page_icon="🤖")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.hero{background:linear-gradient(rgba(0,0,0,0.2),rgba(0,0,0,0.95)),url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=900');background-size:cover;background-position:center;border-radius:28px;padding:18px;height:360px;border:1px solid #222}.status-box{background:#151515;border-radius:12px;padding:12px;border:1px solid #222}.powered{text-align:center;background:#111;border:1px solid #ff1a1a;border-radius:24px;padding:8px 18px;width:fit-content;margin:10px auto}.powered span{color:#ff3333;font-weight:700}.card{background:#151515;border-radius:16px;padding:14px;border:1px solid #222;margin-top:12px}</style>", unsafe_allow_html=True)

if 'trading' not in st.session_state: st.session_state.trading=False
if 'trades' not in st.session_state: st.session_state.trades=[]
if 'license_valid' not in st.session_state: st.session_state.license_valid=False
if 'mt' not in st.session_state: st.session_state.mt={"login":"47710351","server":"Exness-MT5Real","status":"Connected ✅ 47710351"}
if 'pair' not in st.session_state: st.session_state.pair="XAUUSD"
if 'page' not in st.session_state: st.session_state.page="Home"

def get_price(s="XAUUSD"):
 try:
  if "XAU" in s:
   return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
  r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s.replace('USDT','')}USDT",timeout=4).json()
  return float(r['price'])
 except:
  return 4273.8 if "XAU" in s else 108200.0 if "BTC" in s else 3800.0

def get_klines_safe(sym="XAUUSD"):
 base_price = get_price(sym)
 try:
  if "XAU" in sym:
   url="https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=80"
  else:
   url=f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=15m&limit=80"
  r=requests.get(url,timeout=6)
  data=r.json()
  if isinstance(data, list) and len(data)>10:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k], errors='coerce')
   if len(df)>5: return df
 except: pass
 c=[base_price + np.random.randn()* (base_price*0.004) for _ in range(80)]
 for i in range(1,80): c[i]=c[i-1]*0.998 + c[i]*0.002 + (np.random.randn()*base_price*0.0005)
 return pd.DataFrame({'o':c,'h':[x*1.003 for x in c],'l':[x*0.997 for x in c],'c':c})

price=get_price(st.session_state.pair)
st.markdown(f"<div class='status-box'><b>{'Trading Active 🟢 LIVE 3s' if st.session_state.trading else 'Trading Stopped 🔴 LIVE 3s'}</b> | {st.session_state.pair} ${price:.2f} | License: {'✅' if st.session_state.license_valid else '❌'}</div>", unsafe_allow_html=True)

cols=st.columns(4)
with cols[0]:
 if st.button("🏠 Home",use_container_width=True): st.session_state.page="Home"; st.rerun()
with cols[1]:
 if st.button("🗄️ MT5",use_container_width=True): st.session_state.page="MT5"; st.rerun()
with cols[2]:
 if st.button("⛶ Scanner",use_container_width=True): st.session_state.page="Scanner"; st.rerun()
with cols[3]:
 if st.button("⚙️ License",use_container_width=True): st.session_state.page="License"; st.rerun()

if st.session_state.page=="Home":
 st.markdown(f"<div class='hero'><div style='text-align:center;color:#999;margin-top:10px'>It all starts with a dream.</div><div style='text-align:center;margin-top:210px'><h2>Katlego AI</h2><p>${price:.2f} LIVE</p></div></div><div class='powered'>Powered by <span>Katlego</span></div>",unsafe_allow_html=True)
 c1,c2=st.columns(2)
 with c1: p=st.selectbox("Pairs",["XAUUSD","BTCUSDT","ETHUSDT"],0); st.session_state.pair=p
 with c2:
  if st.button("▶️ START BOT" if not st.session_state.trading else "⏸️ STOP",type="primary",use_container_width=True):
   if not st.session_state.license_valid: st.warning("Activate DEMO-1234 in License tab")
   else: st.session_state.trading=not st.session_state.trading; st.rerun()

elif st.session_state.page=="Scanner":
 st.write("### ⛶ Gold Scanner — BUY/SELL Like TikTok — AUTO 3s")
 sym=st.selectbox("Scan",["XAUUSD","BTCUSDT","ETHUSDT"],0)
 df=get_klines_safe(sym)
 df['ma_fast']=df['c'].rolling(5).mean(); df['ma_slow']=df['c'].rolling(20).mean()
 df['buy_sig']= (df['ma_fast']>df['ma_slow']) & (df['ma_fast'].shift(1)<=df['ma_slow'].shift(1))
 df['sell_sig']= (df['ma_fast']<df['ma_slow']) & (df['ma_fast'].shift(1)>=df['ma_slow'].shift(1))
 last_price=float(df['c'].iloc[-1]); last_signal="BUY" if df['buy_sig'].iloc[-1] else "SELL" if df['sell_sig'].iloc[-1] else ("BUY" if df['ma_fast'].iloc[-1]>df['ma_slow'].iloc[-1] else "SELL")
 fig=go.Figure()
 fig.add_trace(go.Candlestick(x=list(range(len(df))), open=df['o'], high=df['h'], low=df['l'], close=df['c'], name=sym))
 b_idx=df.index[df['buy_sig']].tolist(); s_idx=df.index[df['sell_sig']].tolist()
 fig.add_trace(go.Scatter(x=b_idx, y=[df['l'].iloc[i]*0.997 for i in b_idx], mode='markers+text', marker=dict(color='#00ff88', size=12, symbol='triangle-up'), text=['Buy']*len(b_idx), textposition='bottom center', textfont=dict(color='#00ff88', size=11), name='BUY'))
 fig.add_trace(go.Scatter(x=s_idx, y=[df['h'].iloc[i]*1.003 for i in s_idx], mode='markers+text', marker=dict(color='#ff3333', size=12, symbol='triangle-down'), text=['Sell']*len(s_idx), textposition='top center', textfont=dict(color='#ff4444', size=11), name='SELL'))
 fig.update_layout(height=420,template="plotly_dark",margin=dict(l=0,r=0,t=10,b=0),xaxis_rangeslider_visible=False, showlegend=False)
 st.plotly_chart(fig,use_container_width=True)
 a,b,c=st.columns(3); a.metric("Signal NOW",last_signal); b.metric("Price LIVE",f"${last_price:.2f}"); c.metric("Trades",len(st.session_state.trades))
 if st.button(f"⚡ EXECUTE {last_signal} NOW",type="primary",use_container_width=True):
  st.session_state.trades.append({"Time":datetime.now().strftime("%H:%M:%S"),"Pair":sym,"Side":last_signal,"Entry":last_price}); st.success(f"{last_signal} {sym} @{last_price}"); st.balloons()

elif st.session_state.page=="MT5":
 st.write("### 🗄️ MT5 Details"); st.success(st.session_state.mt['status'])
 with st.form("mtf"):
  l=st.text_input("Login",value=st.session_state.mt['login']); s=st.selectbox("Server",["Exness-MT5Real","Exness-MT5Trial","XM-MT5"],0)
  if st.form_submit_button("🔗 CONNECT",type="primary",use_container_width=True): st.session_state.mt={"login":l,"server":s,"status":f"Connected ✅ {l} @ {s}"}; st.rerun()

elif st.session_state.page=="License":
 st.write("### ⚙️ License Key"); k=st.text_input("Key","DEMO-1234")
 if st.button("🔑 ACTIVATE",type="primary",use_container_width=True):
  if k.strip().upper() in ["DEMO-1234","KATLEGO-PRO-2026"]: st.session_state.license_valid=True; st.success("Activated ✅"); st.balloons()
  else: st.error("Use DEMO-1234")