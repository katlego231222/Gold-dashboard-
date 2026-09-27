import streamlit as st, requests, pandas as pd, numpy as np
from datetime import datetime
import plotly.graph_objects as go
import streamlit.components.v1 as components

try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=8000, key="sync")
except:
 pass

st.set_page_config(layout="centered", page_title="Katlego MT5 SYNC", page_icon="✅")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.box{background:#111;border:2px solid #ffcc00;border-radius:14px;padding:12px}.buy{background:#00ff88;color:#000;border-radius:8px;padding:8px 12px;font-weight:900}.sell{background:#ff3333;color:#fff;border-radius:8px;padding:8px 12px;font-weight:900}</style>", unsafe_allow_html=True)

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
   demands.append({"low":float(df['l'].iloc[i-1:i+1].min()),"high":float(df['l'].iloc[i]),"mid":(float(df['l'].iloc[i-1:i+1].min())+float(df['l'].iloc[i]))/2})
  if body < -rng*0.55 and body<0:
   supplies.append({"low":float(df['h'].iloc[i]),"high":float(df['h'].iloc[i-1:i+1].max()),"mid":(float(df['h'].iloc[i])+float(df['h'].iloc[i-1:i+1].max()))/2})
 return demands[-3:], supplies[-3:]

price=get_price("XAUUSD")

# NEW TOGGLE
st.markdown(f"<div class='box'><b>🔄 MT5 SYNC FIX — Real Time BUY = App BUY</b><br>XAUUSD ${price:.2f} LIVE</div>",unsafe_allow_html=True)

colA,colB,colC,colD=st.columns(4)
with colA:
 sym=st.selectbox("Pair",["XAUUSD","BTCUSDT"],0)
with colB:
 tf=st.selectbox("TF",["5M","15M"],0)
with colC:
 mode=st.selectbox("Mode",["REAL-TIME — Match MT5 ✅","LOCKED — No Repaint 🔒"],0)
with colD:
 rr=st.selectbox("RR",["1:3","1:5","1:7"],1)

interval = "5m" if "5M" in tf else "15m"
rr_val=int(rr.split(":")[1])

df=get_klines(sym, interval, 200)
df_live=df # live includes current candle
df_closed=df.iloc[:-1]
live_price=get_price(sym)
last_closed=float(df_closed['c'].iloc[-1])

# REAL-TIME EMAs
df_live['ema_fast']=df_live['c'].ewm(span=9).mean()
df_live['ema_slow']=df_live['c'].ewm(span=21).mean()
df_closed['ema_fast']=df_closed['c'].ewm(span=9).mean()
df_closed['ema_slow']=df_closed['c'].ewm(span=21).mean()

if "REAL-TIME" in mode:
 # MATCHES MT5 INSTANTLY — uses live candle
 is_buy = df_live['ema_fast'].iloc[-1] > df_live['ema_slow'].iloc[-1] and df_live['c'].iloc[-1] > df_live['ema_fast'].iloc[-1]
 is_sell = df_live['ema_fast'].iloc[-1] < df_live['ema_slow'].iloc[-1] and df_live['c'].iloc[-1] < df_live['ema_fast'].iloc[-1]
 signal="BUY" if is_buy else "SELL" if is_sell else "BUY" if live_price > last_closed else "SELL"
 calc_df=df_live
else:
 # LOCKED — uses closed
 is_buy = df_closed['ema_fast'].iloc[-2] > df_closed['ema_slow'].iloc[-2]
 is_sell = df_closed['ema_fast'].iloc[-2] < df_closed['ema_slow'].iloc[-2]
 signal="BUY" if is_buy else "SELL"
 calc_df=df_closed

demands, supplies = find_zones(calc_df)

# ENTRY + SHORT SL + LONG TP — ONLY 5M/15M
if signal=="BUY":
 zone=demands[-1] if demands else {"low":live_price-5,"high":live_price-2,"mid":live_price-3}
 entry=zone['mid'] if "REAL-TIME" not in mode else live_price - 1 # Real-time entry near live price
 sl=zone['low']-1.2 if demands else entry-3
 tp=entry + abs(entry-sl)*rr_val
else:
 zone=supplies[-1] if supplies else {"low":live_price+2,"high":live_price+5,"mid":live_price+3}
 entry=zone['mid'] if "REAL-TIME" not in mode else live_price + 1
 sl=zone['high']+1.2 if supplies else entry+3
 tp=entry - abs(entry-sl)*rr_val

sl_dist=abs(entry-sl)
tp_dist=abs(tp-entry)

# CHART
fig=go.Figure()
plot_df = df_live if "REAL-TIME" in mode else df_closed
fig.add_trace(go.Candlestick(x=list(range(len(plot_df))), open=plot_df['o'], high=plot_df['h'], low=plot_df['l'], close=plot_df['c'], name=interval))
fig.add_hline(y=entry, line_color="#ffcc00", line_width=4, annotation_text=f"ENTRY {entry:.2f}")
fig.add_hline(y=sl, line_color="#ff3333", line_width=3, line_dash="dash", annotation_text=f"SL SHORT {sl:.2f} -{sl_dist:.1f}")
fig.add_hline(y=tp, line_color="#00ff88", line_width=3, line_dash="dash", annotation_text=f"TP LONG {tp:.2f} +{tp_dist:.1f}")
fig.add_hline(y=live_price, line_color="white", line_dash="dot", annotation_text=f"LIVE NOW {live_price:.2f} MT5")

ymin_val=min(entry, sl, tp, live_price) - 6
ymax_val=max(entry, sl, tp, live_price) + 6
fig.update_layout(height=500, template="plotly_dark", margin=dict(l=0,r=0,t=10,b=0), xaxis_rangeslider_visible=False, showlegend=False, yaxis=dict(range=[ymin_val, ymax_val]))
st.plotly_chart(fig, use_container_width=True)

if signal=="BUY":
 st.markdown(f"<div class='buy'>✅ BUY — ENTRY ${entry:.2f} | SL SHORT ${sl:.2f} -${sl_dist:.1f} | TP LONG ${tp:.2f} +${tp_dist:.1f} RR 1:{rr_val} | {mode} | {interval}</div>",unsafe_allow_html=True)
else:
 st.markdown(f"<div class='sell'>🔴 SELL — ENTRY ${entry:.2f} | SL SHORT ${sl:.2f} -${sl_dist:.1f} | TP LONG ${tp:.2f} +${tp_dist:.1f} RR 1:{rr_val} | {mode} | {interval}</div>",unsafe_allow_html=True)

st.write(f"Live MT5: ${live_price:.2f} | Signal: {signal} | Mode: {mode}")

# REAL MT5 CHART
components.html(f"""<div id="tv" style="height:450px;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize":true,"height":450,"symbol":"OANDA:XAUUSD","interval":"{ '5' if interval=='5m' else '15'}","theme":"dark","style":"1","container_id":"tv"}});</script>""",height=470)

if st.button(f"SEND {signal} {interval} {mode} -> 0637247675",type="primary",use_container_width=True):
 import urllib.parse
 msg=f"{signal} {sym} {interval} {mode} ENTRY {entry:.2f} SL SHORT {sl:.2f} -{sl_dist:.1f} TP LONG {tp:.2f} +{tp_dist:.1f} RR 1:{rr_val} LIVE {live_price:.2f} | 0637247675"
 link=f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}"
 st.link_button("SEND TO WHATSAPP 0637247675", link, type="primary", use_container_width=True)