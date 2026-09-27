import streamlit as st, requests, pandas as pd, numpy as np
from datetime import datetime
import plotly.graph_objects as go
import streamlit.components.v1 as components

try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=10000, key="5m15m")
except: pass

st.set_page_config(layout="centered", page_title="Katlego 5M 15M LOCKED", page_icon="🔒")

st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.box{background:#111;border:2px solid #00ff88;border-radius:14px;padding:12px}.entry{background:#ffcc00;color:#000;border-radius:8px;padding:8px 12px;font-weight:900}.sl{background:#ff3333;color:#fff;border-radius:8px;padding:8px 12px;font-weight:900}.tp{background:#00ff88;color:#000;border-radius:8px;padding:8px 12px;font-weight:900}</style>", unsafe_allow_html=True)

if 'lock_sig' not in st.session_state: st.session_state.lock_sig=None
if 'lock_entry' not in st.session_state: st.session_state.lock_entry=None
if 'lock_sl' not in st.session_state: st.session_state.lock_sl=None
if 'lock_tp' not in st.session_state: st.session_state.lock_tp=None
if 'lock_time' not in st.session_state: st.session_state.lock_time=None

MY_PHONE="27637247675"

def get_price(s="XAUUSD"):
 try:
  if "XAU" in s: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
  return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}",timeout=4).json()['price'])
 except: return 4259.0

def get_klines(sym, interval, limit=200):
 base=get_price(sym)
 try:
  url=f"https://api.binance.com/api/v3/klines?symbol={'PAXGUSDT' if 'XAU' in sym else sym}&interval={interval}&limit={limit}"
  data=requests.get(url,timeout=6).json()
  if isinstance(data,list) and len(data)>20:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k], errors='coerce')
   return df
 except: pass
 c=[base+np.random.randn()*base*0.0006 for _ in range(limit)]
 for i in range(1,limit): c[i]=c[i-1]*0.9997+c[i]*0.0003
 return pd.DataFrame({'o':c,'h':[x*1.002 for x in c],'l':[x*0.998 for x in c],'c':c})

def find_zones_5_15(df):
 demands=[]; supplies=[]
 for i in range(20, len(df)-2): # CLOSED only
  body=df['c'].iloc[i]-df['o'].iloc[i]
  rng=df['h'].iloc[i-10:i].max() - df['l'].iloc[i-10:i].min()
  if body > rng*0.55 and body>0:
   demands.append({"low":float(df['l'].iloc[i-1:i+1].min()),"high":float(df['l'].iloc[i]),"mid":float((df['l'].iloc[i-1:i+1].min()+df['l'].iloc[i])/2),"idx":i})
  if body < -rng*0.55 and body<0:
   supplies.append({"low":float(df['h'].iloc[i]),"high":float(df['h'].iloc[i-1:i+1].max()),"mid":float((df['h'].iloc[i]+df['h'].iloc[i-1:i+1].max())/2),"idx":i})
 return demands[-3:], supplies[-3:]

price=get_price("XAUUSD")
st.markdown(f"<div class='box'><b>🔒 5M & 15M ONLY — ENTRY + SHORT SL + LONG TP — NO REPAINT</b><br>XAUUSD ${price:.2f} | HTF 15M Trend | LTF 5M Entry | WA 0637247675</div>",unsafe_allow_html=True)

col1,col2,col3=st.columns(3)
with col1: sym=st.selectbox("Pair",["XAUUSD","BTCUSDT"],0)
with col2: tf=st.selectbox("Timeframe",["5M Entry — Fast ⚡","15M Entry — Accurate 🎯"],0)
with col3: rr=st.selectbox("RR",["1:3","1:5 🚀","1:7 💎"],1)
interval = "5m" if "5M" in tf else "15m"
rr_val=int(rr.split(":")[1][0])
# HTF is always 15m for trend
df_htf=get_klines(sym, "15m", 150)
df_htf['ema20']=df_htf['c'].ewm(span=20).mean(); df_htf['ema50']=df_htf['c'].ewm(span=50).mean()
htf_trend="BULL" if df_htf['ema20'].iloc[-2] > df_htf['ema50'].iloc[-2] else "BEAR"

df=get_klines(sym, interval, 200)
df_closed=df.iloc[:-1] # CLOSED CANDLES ONLY = NO REPAINT
live_price=get_price(sym)
last_closed=float(df_closed['c'].iloc[-1])

# CRT Levels on 15m
pdh=float(df_closed['h'].iloc[-20:].max()); pdl=float(df_closed['l'].iloc[-20:].min())

demands, supplies = find_zones_5_15(df_closed)

# LOCKED SIGNAL on CLOSED candle
df_closed['ema_fast']=df_closed['c'].ewm(span=9).mean()
df_closed['ema_slow']=df_closed['c'].ewm(span=21).mean()
bull_cross = df_closed['ema_fast'].iloc[-2] > df_closed['ema_slow'].iloc[-2] and df_closed['ema_fast'].iloc[-3] <= df_closed['ema_slow'].iloc[-3]
bear_cross = df_closed['ema_fast'].iloc[-2] < df_closed['ema_slow'].iloc[-2] and df_closed['ema_fast'].iloc[-3] >= df_closed['ema_slow'].iloc[-3]

new_signal=None
if htf_trend=="BULL" and bull_cross: new_signal="BUY"
elif htf_trend=="BEAR" and bear_cross: new_signal="SELL"
else: new_signal=st.session_state.lock_sig # keep old

# LOCK if new
if st.session_state.lock_sig is None or (new_signal!=st.session_state.lock_sig and new_signal in ["BUY","SELL"] and (bull_cross or bear_cross)):
 if new_signal=="BUY" and demands:
  zone=demands[-1]; entry=zone['mid']; sl=zone['low']-1.5; tp=entry+abs(entry-sl)*rr_val
 elif new_signal=="SELL" and supplies:
  zone=supplies[-1]; entry=zone['mid']; sl=zone['high']+1.5; tp=entry-abs(entry-sl)*rr_val
 else:
  # fallback tight levels for 5/15m
  if new_signal=="BUY": entry=last_closed-2; sl=entry-3; tp=entry+3*rr_val
  else: entry=last_closed+2; sl=entry+3; tp=entry-3*rr_val
 st.session_state.lock_sig=new_signal; st.session_state.lock_entry=entry; st.session_state.lock_sl=sl; st.session_state.lock_tp=tp
 st.session_state.lock_time=datetime.now().strftime("%H:%M:%S CLOSED")

# Use locked
signal=st.session_state.lock_sig; entry=st.session_state.lock_entry; sl=st.session_state.lock_sl; tp=st.session_state.lock_tp
if signal is None: signal=htf_trend=="BULL" and "BUY" or "SELL"; entry=last_closed; sl=entry-3 if signal=="BUY" else entry+3; tp=entry+3*rr_val if signal=="BUY" else entry-3*rr_val

sl_dist=abs(entry-sl); tp_dist=abs(tp-entry)

# CHART
fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_closed))), open=df_closed['o'], high=df_closed['h'], low=df_closed['l'], close=df_closed['c'], name=f"{interval} CLOSED"))
for d in demands: fig.add_hrect(y0=d['low'], y1=d['high'], fillcolor="rgba(0,255,136,0.18)", line_width=0)
for s in supplies: fig.add_hrect(y0=s['low'], y1=s['high'], fillcolor="rgba(255,51,51,0.18)", line_width=0)
fig.add_hline(y=pdh, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDH {pdh:.2f}")
fig.add_hline(y=pdl, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDL {pdl:.2f}")
fig.add_hline(y=entry, line_color="#ffcc00", line_width=4, annotation_text=f"🔒 ENTRY {entry:.2f} {interval}")
fig.add_hline(y=sl, line_color="#ff3333", line_width=3, line_dash="dash", annotation_text=f"🔒 SL SHORT {sl:.2f} -${sl_dist:.1f}")
fig.add_hline(y=tp, line_color="#00ff88", line_width=3, line_dash="dash", annotation_text=f"🔒 TP LONG {tp:.2f} +${tp_dist:.1f} 1:{rr_val}")
fig.add_hline(y=live_price, line_color="white", line_dash="dot", annotation_text=f"LIVE {live_price:.2f}")
# Auto zoom to show all levels
ymin=min(entry,sl,tp,live_price,pdl)-5; ymax=max(entry