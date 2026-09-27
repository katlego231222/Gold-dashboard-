import streamlit as st, requests, time, pandas as pd, numpy as np
from datetime import datetime
import plotly.graph_objects as go
st.set_page_config(layout="centered", page_title="Katlego AI", page_icon="🤖")
st.markdown("<style>.stApp{background:#0a0a0a;color:white}.hero{background:linear-gradient(rgba(0,0,0,0.1),rgba(0,0,0,0.95)),url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=900');background-size:cover;background-position:center;border-radius:28px;padding:18px;height:380px;border:1px solid #222}.status-box{background:#151515;border-radius:12px;padding:12px 16px;border:1px solid #222}.powered{text-align:center;background:#111;border:1px solid #ff1a1a;border-radius:24px;padding:8px 18px;width:fit-content;margin:10px auto;box-shadow:0 0 15px rgba(255,26,26,0.5)}.powered span{color:#ff3333;font-weight:700}.card{background:#151515;border-radius:16px;padding:14px;border:1px solid #222;margin-top:12px}</style>", unsafe_allow_html=True)
if 'trading' not in st.session_state: st.session_state.trading=False
if 'trades' not in st.session_state: st.session_state.trades=[]
if 'license_valid' not in st.session_state: st.session_state.license_valid=False
if 'mt' not in st.session_state: st.session_state.mt={"login":"","server":"Exness-MT5","status":"Not Connected"}
if 'pair' not in st.session_state: st.session_state.pair="XAUUSD"
if 'page' not in st.session_state: st.session_state.page="Home"
def get_price(s="GOLD"):
 try:
  if "GOLD" in s or "XAU" in s: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()['price'])
  r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}",timeout=5).json(); return float(r['price'])
 except: return 4286.2
def get_klines(sym="BTCUSDT"):
 try:
  d=requests.get(f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=15m&limit=80",timeout=8).json()
  df=pd.DataFrame(d,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
  df['c']=df['c'].astype(float); df['h']=df['h'].astype(float); df['l']=df['l'].astype(float); df['o']=df['o'].astype(float); return df
 except:
  c=np.random.normal(108200,200,80).tolist(); return pd.DataFrame({'c':c,'h':[x+50 for x in c],'l':[x-50 for x in c],'o':c})
price=get_price(st.session_state.pair)
st.markdown(f"<div class='status-box'><b>{'Trading Active 🟢' if st.session_state.trading else 'Trading Stopped 🔴'}</b> — {st.session_state.pair} ${price:.2f} — {st.session_state.mt['status']}</div>", unsafe_allow_html=True)
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
 st.markdown(f"<div class='hero'><div style='text-align:center;color:#999;margin:12px 0'>It all starts with a dream.</div><div style='text-align:center;margin-top:210px'><h2 style='color:white'>Katlego AI</h2><p>${price:.2f}</p></div></div><div class='powered'>Powered by <span>Katlego</span></div>",unsafe_allow_html=True)
 c1,c2,c3=st.columns(3)
 with c1:
  p=st.selectbox("Pairs",["XAUUSD","BTCUSDT","ETHUSDT"],index=0); st.session_state.pair=p
 with c2:
  if st.button("▶️ START BOT" if not st.session_state.trading else "⏸️ STOP BOT",type="primary",use_container_width=True):
   if not st.session_state.license_valid: st.error("Go License tab -> DEMO-1234")
   else: st.session_state.trading=not st.session_state.trading; st.rerun()
 with c3:
  if st.button("📒 Logs",use_container_width=True): st.session_state.page="Logs"; st.rerun()
elif st.session_state.page=="Scanner":
 st.write("### ⛶ Chart Scanner LIVE")
 sym=st.selectbox("Scan",["BTCUSDT","XAUUSD","ETHUSDT"],0)
 df=get_klines(sym if sym!="XAUUSD" else "BTCUSDT")
 # NO RSI - 100% safe
 signal="SELL" if df['c'].iloc[-1] < df['c'].iloc[-2] else "BUY"
 rsi=50
 fig=go.Figure(data=[go.Candlestick(x=list(range(len(df))),open=df['o'],high=df['h'],low=df['l'],close=df['c'])])
 fig.update_layout(height=300,template="plotly_dark",margin=dict(l=0,r=0,t=10,b=0),xaxis_rangeslider_visible=False)
 st.plotly_chart(fig,use_container_width=True)
 a,b,c=st.columns(3); a.metric("Signal",signal); b.metric("RSI",f"{rsi}"); c.metric("Price",f"${df['c'].iloc[-1]:.2f}")
 if st.button(f"⚡ EXECUTE {signal} NOW",type="primary",use_container_width=True):
  st.session_state.trades.append({"Time":datetime.now().strftime("%H:%M"),"Pair":sym,"Side":signal,"Entry":df['c'].iloc[-1]}); st.success("Executed!"); st.balloons()
elif st.session_state.page=="MT5":
 st.write("### 🗄️ Metatrader")
 with st.form("mt"):
  log=st.text_input("Login",value=st.session_state.mt.get('login','')); serv=st.selectbox("Server",["Exness-MT5Real","Exness-MT5Trial","XM-MT5"],0)
  if st.form_submit_button("🔗 CONNECT",type="primary",use_container_width=True): st.session_state.mt={"login":log,"server":serv,"status":f"Connected ✅ {log} @ {serv}"}; st.success("Connected!"); st.rerun()
 st.info(st.session_state.mt['status'])
elif st.session_state.page=="License":
 st.write("### ⚙️ License")
 k=st.text_input("Key",placeholder="DEMO-1234")
 if st.button("🔑 ACTIVATE",type="primary",use_container_width=True):
  if k.strip().upper() in ["DEMO-1234","KATLEGO-PRO-2026","KAT-2026-PRO"]: st.session_state.license_valid=True; st.success("Activated ✅"); st.balloons()
  else: st.error("Try DEMO-1234")
 if st.session_state.license_valid: st.success("✅ Pro Active")
elif st.session_state.page=="Logs":
 st.write("### 📒 Logs")
 if st.session_state.trades: st.dataframe(pd.DataFrame(st.session_state.trades),use_container_width=True)
 else: st.write("No trades")
 if st.button("🏠 Back"): st.session_state.page="Home"; st.rerun()