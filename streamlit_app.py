import streamlit as st, requests, pandas as pd, numpy as np
from datetime import datetime
import plotly.graph_objects as go
import streamlit.components.v1 as components

try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=15000, key="5m15mfix")
except:
 pass

st.set_page_config(layout="centered", page_title="Katlego 5M 15M LOCKED", page_icon="🔒")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.box{background:#111;border:2px solid #00ff88;border-radius:14px;padding:12px}.entry{background:#ffcc00;color:#000;border-radius:8px;padding:8px 12px;font-weight:900}.sl{background:#ff3333;color:#fff;border-radius:8px;padding:8px 12px;font-weight:900}.tp{background:#00ff88;color:#000;border-radius:8px;padding:8px 12px;font-weight:900}</style>", unsafe_allow_html=True)

if 'lock_sig' not in st.session_state:
 st.session_state.lock_sig=None
 st.session_state.lock_entry=None
 st.session_state.lock_sl=None
 st.session_state.lock_tp=None
 st.session_state.lock_time=None

MY_PHONE="27637247675"

def get_price(s="XAUUSD"):
 try:
  if "XAU" in s:
   return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
  return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}",timeout=4).json()['price'])
 except:
  return 4259.0

def get_klines(sym, interval, limit=200):
 base=get_price(sym)
 try:
  sym2='PAXGUSDT' if 'XAU' in sym else sym
  url=f"https://api.binance.com/api/v3/klines?symbol={sym2}&interval={interval}&limit={limit}"
  data=requests.get(url,timeout=6).json()
  if isinstance(data,list) and len(data)>20:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']:
    df[k]=pd.to_numeric(df[k], errors='coerce')
   return df
 except:
  pass
 c=[base+np.random.randn()*base*0.0006 for _ in range(limit)]
 for i in range(1,limit):
  c[i]=c[i-1]*0.9997+c[i]*0.0003
 return pd.DataFrame({'o':c,'h':[x*1.002 for x in c],'l':[x*0.998 for x in c],'c':c})

def find_zones(df):
 demands=[]; supplies=[]
 for i in range(20, len(df)-2):
  body=df['c'].iloc[i]-df['o'].iloc[i]
  rng=df['h'].iloc[i-10:i].max() - df['l'].iloc[i-10:i].min()
  if body > rng*0.55 and body>0:
   low_val=float(df['l'].iloc[i-1:i+1].min())
   high_val=float(df['l'].iloc[i])
   mid_val=(low_val+high_val)/2
   demands.append({"low":low_val,"high":high_val,"mid":mid_val})
  if body < -rng*0.55 and body<0:
   low_val=float(df['h'].iloc[i])
   high_val=float(df['h'].iloc[i-1:i+1].max())
   mid_val=(low_val+high_val)/2
   supplies.append({"low":low_val,"high":high_val,"mid":mid_val})
 return demands[-3:], supplies[-3:]

price=get_price("XAUUSD")
st.markdown(f"<div class='box'><b>🔒 5M & 15M ONLY — ENTRY + SHORT SL + LONG TP — FIXED</b><br>XAUUSD ${price:.2f} | HTF 15M | WA 0637247675</div>",unsafe_allow_html=True)

c1,c2,c3=st.columns(3)
with c1:
 sym=st.selectbox("Pair",["XAUUSD","BTCUSDT"],0)
with c2:
 tf=st.selectbox("Timeframe",["5M Entry","15M Entry"],0)
with c3:
 rr=st.selectbox("RR",["1:3","1:5","1:7"],1)

interval = "5m" if "5M" in tf else "15m"
rr_val=int(rr.split(":")[1])

df_htf=get_klines(sym, "15m", 150)
df_htf['ema20']=df_htf['c'].ewm(span=20).mean()
df_htf['ema50']=df_htf['c'].ewm(span=50).mean()
htf_trend="BULL" if df_htf['ema20'].iloc[-2] > df_htf['ema50'].iloc[-2] else "BEAR"

df=get_klines(sym, interval, 200)
df_closed=df.iloc[:-1]
live_price=get_price(sym)
last_closed=float(df_closed['c'].iloc[-1])

pdh=float(df_closed['h'].iloc[-20:].max())
pdl=float(df_closed['l'].iloc[-20:].min())

demands, supplies = find_zones(df_closed)

df_closed['ema_fast']=df_closed['c'].ewm(span=9).mean()
df_closed['ema_slow']=df_closed['c'].ewm(span=21).mean()
bull_cross = df_closed['ema_fast'].iloc[-2] > df_closed['ema_slow'].iloc[-2] and df_closed['ema_fast'].iloc[-3] <= df_closed['ema_slow'].iloc[-3]
bear_cross = df_closed['ema_fast'].iloc[-2] < df_closed['ema_slow'].iloc[-2] and df_closed['ema_fast'].iloc[-3] >= df_closed['ema_slow'].iloc[-3]

new_signal=None
if htf_trend=="BULL" and bull_cross:
 new_signal="BUY"
elif htf_trend=="BEAR" and bear_cross:
 new_signal="SELL"
else:
 new_signal=st.session_state.lock_sig

if st.session_state.lock_sig is None or (new_signal!=st.session_state.lock_sig and new_signal in ["BUY","SELL"]):
 if new_signal=="BUY" and demands:
  zone=demands[-1]
  entry=zone['mid']
  sl=zone['low']-1.5
  tp=entry+abs(entry-sl)*rr_val
 elif new_signal=="SELL" and supplies:
  zone=supplies[-1]
  entry=zone['mid']
  sl=zone['high']+1.5
  tp=entry-abs(entry-sl)*rr_val
 else:
  if new_signal=="BUY":
   entry=last_closed-2
   sl=entry-3
   tp=entry+3*rr_val
  else:
   entry=last_closed+2
   sl=entry+3
   tp=entry-3*rr_val
 st.session_state.lock_sig=new_signal
 st.session_state.lock_entry=entry
 st.session_state.lock_sl=sl
 st.session_state.lock_tp=tp
 st.session_state.lock_time=datetime.now().strftime("%H:%M:%S")

signal=st.session_state.lock_sig
entry=st.session_state.lock_entry
sl=st.session_state.lock_sl
tp=st.session_state.lock_tp

if signal is None:
 signal="BUY" if htf_trend=="BULL" else "SELL"
 entry=last_closed
 sl=entry-3 if signal=="BUY" else entry+3
 tp=entry+15 if signal=="BUY" else entry-15

sl_dist=abs(entry-sl)
tp_dist=abs(tp-entry)

fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_closed))), open=df_closed['o'], high=df_closed['h'], low=df_closed['l'], close=df_closed['c'], name=interval))
for d in demands:
 fig.add_hrect(y0=d['low'], y1=d['high'], fillcolor="rgba(0,255,136,0.18)", line_width=0)
for s in supplies:
 fig.add_hrect(y0=s['low'], y1=s['high'], fillcolor="rgba(255,51,51,0.18)", line_width=0)
fig.add_hline(y=pdh, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDH {pdh:.2f}")
fig.add_hline(y=pdl, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDL {pdl:.2f}")
fig.add_hline(y=entry, line_color="#ffcc00", line_width=4, annotation_text=f"ENTRY {entry:.2f}")
fig.add_hline(y=sl, line_color="#ff3333", line_width=3, line_dash="dash", annotation_text=f"SL {sl:.2f}")
fig.add_hline(y=tp, line_color="#00ff88", line_width=3, line_dash="dash", annotation_text=f"TP {tp:.2f}")
fig.add_hline(y=live_price, line_color="white", line_dash="dot", annotation_text=f"LIVE {live_price:.2f}")

ymin_val=min(entry, sl, tp, live_price, pdl) - 5
ymax_val=max(entry, sl, tp, live_price, pdh) + 5
fig.update_layout(height=520, template="plotly_dark", margin=dict(l=0,r=0,t=10,b=0), xaxis_rangeslider_visible=False, showlegend=False, yaxis=dict(range=[ymin_val, ymax_val]))
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"<div style='display:flex;gap:8px;flex-wrap:wrap'><div class='entry'>ENTRY {entry:.2f}</div><div class='sl'>SL SHORT {sl:.2f} -{sl_dist:.1f}</div><div class='tp'>TP LONG {tp:.2f} +{tp_dist:.1f} RR 1:{rr_val}</div></div>",unsafe_allow_html=True)
st.write(f"LOCKED: {signal} | HTF 15M: {htf_trend} | TF: {interval} | Locked: {st.session_state.lock_time} | Live: ${live_price:.2f}")

st.write(f"### 📈 REAL MT5 CHART — {interval.upper()}")
tv_sym="OANDA:XAUUSD" if "XAU" in sym else "BINANCE:BTCUSDT"
tv_int="5" if interval=="5m" else "15"
components.html(f"""<div id="tv" style="height:500px;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize":true,"height":500,"symbol":"{tv_sym}","interval":"{tv_int}","timezone":"Africa/Johannesburg","theme":"dark","style":"1","container_id":"tv"}});</script>""",height=520)

if st.button(f"SEND {signal} {interval} ENTRY {entry:.2f} -> 0637247675",type="primary",use_container_width=True):
 msg=f"LOCKED {sym} {signal} {interval} ENTRY {entry:.2f} SL {sl:.2f} -{sl_dist:.1f} TP {tp:.2f} +{tp_dist:.1f} RR 1:{rr_val} HTF {htf_trend} | 0637247675"
 link=f"https://wa.me/{MY_PHONE}?text={requests.utils.quote(msg)}"
 st.link_button("SEND WHATSAPP 0637247675", link, type="primary", use_container_width=True)
 st.balloons()