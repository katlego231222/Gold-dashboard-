import streamlit as st, requests, pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(layout="centered", page_title="LONG TP SHORT SL FIXED", page_icon="💎")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}</style>", unsafe_allow_html=True)

def get_price():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
 except: return 4266.30

def get_klines(interval, limit=200):
 try:
  data=requests.get(f"https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval={interval}&limit={limit}",timeout=5).json()
  if isinstance(data,list) and len(data)>20:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k])
   return df
 except: pass
 import numpy as np
 base=get_price()
 c=[base]*limit
 return pd.DataFrame({'o':c,'h':[x*1.001 for x in c],'l':[x*0.999 for x in c],'c':c})

live=get_price()
st.success(f"XAUUSD ${live:.2f} LIVE | 5M 15M 1H | LONG TP SHORT SL | 0637247675")

tf = st.selectbox("Timeframe",["5M","15M","1H"],1)
rr = st.selectbox("RR",["1:7","1:5","1:3"],0)
mode = st.selectbox("Mode",["REAL-TIME","LOCKED"],0)

# SAFE RR - NO EMOJI BUG
rr_val = 7 if "7" in rr else 5 if "5" in rr else 3
interval = {"5M":"5m","15M":"15m","1H":"1h"}[tf]
tv_int = {"5M":"5","15M":"15","1H":"60"}[tf]

df=get_klines(interval)
df_c=df.iloc[:-1]

# CRT + S&D
pdh=float(df_c['h'].iloc[-40:].max()); pdl=float(df_c['l'].iloc[-40:].min())
demands=[]; supplies=[]
for i in range(20, len(df_c)-3):
 b=df_c['c'].iloc[i]-df_c['o'].iloc[i]
 r=df_c['h'].iloc[i-8:i].max() - df_c['l'].iloc[i-8:i].min()
 if b > r*0.6: demands.append({"low":float(df_c['l'].iloc[i-1]),"high":float(df_c['l'].iloc[i]),"mid":float(df_c['l'].iloc[i-1]+df_c['l'].iloc[i])/2})
 if b < -r*0.6: supplies.append({"low":float(df_c['h'].iloc[i]),"high":float(df_c['h'].iloc[i-1]),"mid":float(df_c['h'].iloc[i]+df_c['h'].iloc[i-1])/2})

use=df if mode=="REAL-TIME" else df_c
use['e9']=use['c'].ewm(9).mean(); use['e21']=use['c'].ewm(21).mean()
e9=float(use['e9'].iloc[-1]); e21=float(use['e21'].iloc[-1])

if demands and e9>e21:
 sig="BUY"; z=demands[-1]; entry=z['mid']; sl=z['low']-0.8
else:
 sig="SELL"; z=supplies[-1] if supplies else {"mid":live+2,"low":live+1,"high":live+3}; entry=z['mid']; sl=z['high']+0.8

if abs(entry-sl)>4:
 sl=entry-3 if sig=="BUY" else entry+3
if mode=="REAL-TIME" and abs(live-entry)>6:
 entry=live-0.5 if sig=="BUY" else live+0.5
 sl=entry-2.8 if sig=="BUY" else entry+2.8

tp = entry + abs(entry-sl)*rr_val if sig=="BUY" else entry - abs(entry-sl)*rr_val
sl_d=abs(entry-sl); tp_d=abs(tp-entry)

fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_c))), open=df_c['o'], high=df_c['h'], low=df_c['l'], close=df_c['c']))
fig.add_hline(y=entry, line_color="yellow", line_width=3, annotation_text=f"ENTRY {entry:.2f}")
fig.add_hline(y=sl, line_color="red", line_width=2, line_dash="dash", annotation_text=f"SL SHORT {sl:.2f} -{sl_d:.1f}")
fig.add_hline(y=tp, line_color="#00ff88", line_width=2, line_dash="dash", annotation_text=f"TP LONG {tp:.2f} +{tp_d:.1f} RR 1:{rr_val}")
fig.add_hline(y=live, line_color="white", line_dash="dot", annotation_text=f"LIVE {live:.2f}")
fig.update_layout(height=380, template="plotly_dark", margin=dict(l=0,r=0,t=5,b=0), xaxis_rangeslider_visible=False, yaxis=dict(range=[min(entry,sl,tp,live)-6, max(entry,sl,tp,live)+6]))
st.plotly_chart(fig, use_container_width=True)

st.metric(f"{sig} {tf}", f"ENTRY ${entry:.2f}", f"SL -${sl_d:.1f} TIGHT | TP +${tp_d:.1f} LONG RR 1:{rr_val}")

# TRADINGVIEW WITH LEVELS
st.write(f"### TRADINGVIEW {tf} — ENTRY / SL SHORT / TP LONG DRAWN")
components.html(f"""
<div id="tv" style="height:550px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
var w=new TradingView.widget({{"autosize":true,"height":550,"symbol":"OANDA:XAUUSD","interval":"{tv_int}","timezone":"Africa/Johannesburg","theme":"dark","container_id":"tv"}});
w.onChartReady(function(){{
 var c=w.chart();
 c.createOrderLine().setText("ENTRY {entry:.2f}").setPrice({entry}).setLineColor("yellow").setLineWidth(3);
 c.createOrderLine().setText("SL SHORT {sl:.2f} -{sl_d:.1f}").setPrice({sl}).setLineColor("red").setLineWidth(2);
 c.createOrderLine().setText("TP LONG {tp:.2f} +{tp_d:.1f} RR 1:{rr_val}").setPrice({tp}).setLineColor("#00ff88").setLineWidth(2);
 c.createPositionLine().setText("LIVE {live:.2f}").setPrice({live}).setLineColor("white");
}});
</script>
""", height=570)

if st.button(f"SEND {sig} ENTRY {entry:.2f} SL {sl:.2f} TP {tp:.2f} -> 0637247675",type="primary",use_container_width=True):
 import urllib.parse
 msg=f"{sig} {tf} ENTRY {entry:.2f} SL SHORT {sl:.2f} -{sl_d:.1f} TIGHT TP LONG {tp:.2f} +{tp_d:.1f} RR 1:{rr_val} LIVE {live:.2f} | TV drawn | 0637247675"
 st.link_button("SEND WHATSAPP", f"https://wa.me/27637247675?text={urllib.parse.quote(msg)}", type="primary", use_container_width=True)