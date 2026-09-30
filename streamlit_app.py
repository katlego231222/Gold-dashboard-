import streamlit as st, requests, pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go
from datetime import datetime
try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=8000, key="tp123_alert")
except: pass

st.set_page_config(layout="centered", page_title="TP1 TP2 TP3 SYSTEM", page_icon="💎")
if 'alert_fired' not in st.session_state: st.session_state.alert_fired=False
if 'last_entry' not in st.session_state: st.session_state.last_entry=0

MY_PHONE="27637247675"

def get_price():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
 except: return 4260.70

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
st.success(f"💎 TP1 TP2 TP3 + ENTRY HIT ALERT | XAUUSD ${live:.2f} LIVE | 5M 15M 1H | LONG TP SHORT SL")

tf = st.selectbox("Timeframe",["5M","15M","1H"],1)
rr_main = st.selectbox("Main RR (TP3)",["1:7","1:5","1:3"],0)
mode = st.selectbox("Mode",["REAL-TIME","LOCKED"],0)
rr3 = 7 if "7" in rr_main else 5 if "5" in rr_main else 3
rr1, rr2 = 2, 4 # TP1 = 1:2, TP2 = 1:4, TP3 = 1:7/5/3
if rr3==3: rr1, rr2 = 1, 2
if rr3==5: rr1, rr2 = 2, 4

interval = {"5M":"5m","15M":"15m","1H":"1h"}[tf]
tv_int = {"5M":"5","15M":"15","1H":"60"}[tf]

df=get_klines(interval); df_c=df.iloc[:-1]

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

if abs(entry-sl)>4: sl=entry-3 if sig=="BUY" else entry+3
if mode=="REAL-TIME" and abs(live-entry)>6:
 entry=live-0.5 if sig=="BUY" else live+0.5
 sl=entry-2.8 if sig=="BUY" else entry+2.8

sl_d=abs(entry-sl)
# --- TP1 TP2 TP3 CALCULATION ---
if sig=="BUY":
 tp1 = entry + sl_d*rr1
 tp2 = entry + sl_d*rr2
 tp3 = entry + sl_d*rr3
else:
 tp1 = entry - sl_d*rr1
 tp2 = entry - sl_d*rr2
 tp3 = entry - sl_d*rr3

tp1_d, tp2_d, tp3_d = abs(tp1-entry), abs(tp2-entry), abs(tp3-entry)

# --- ENTRY HIT ALERT ---
dist=abs(live-entry)
entry_hit=dist<=0.7
if abs(st.session_state.last_entry-entry)>1.0:
 st.session_state.alert_fired=False
 st.session_state.last_entry=entry

if entry_hit and not st.session_state.alert_fired:
 st.session_state.alert_fired=True
 st.balloons()
 st.markdown(f"<div style='background:#ffcc00;color:#000;border-radius:12px;padding:14px;font-weight:900;font-size:18px'>🔔 ENTRY HIT! {sig} ENTRY ${entry:.2f} | TP1 ${tp1:.2f} TP2 ${tp2:.2f} TP3 ${tp3:.2f}</div>", unsafe_allow_html=True)
 components.html(f"<audio autoplay><source src='https://cdn.pixabay.com/download/audio/2022/03/24/audio_1a7dfe20f3.mp3' type='audio/mpeg'></audio><script>alert('🔔 ENTRY HIT! {sig} {entry:.2f} HIT!\\nTP1 {tp1:.2f} TP2 {tp2:.2f} TP3 {tp3:.2f}\\nGO MT5!');</script>", height=0)
else:
 st.info(f"Monitoring ENTRY — ENTRY ${entry:.2f} LIVE ${live:.2f} Dist ${dist:.1f} | TP1 +${tp1_d:.1f} TP2 +${tp2_d:.1f} TP3 +${tp3_d:.1f} | Alert within $0.70")

if st.button("Reset Alert"): st.session_state.alert_fired=False; st.rerun()

# Chart with 3 TPs
fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_c))), open=df_c['o'], high=df_c['h'], low=df_c['l'], close=df_c['c']))
fig.add_hline(y=entry, line_color="yellow", line_width=4, annotation_text=f"ENTRY {entry:.2f}")
fig.add_hline(y=sl, line_color="red", line_width=2, line_dash="dash", annotation_text=f"SL SHORT {sl:.2f} -{sl_d:.1f}")
fig.add_hline(y=tp1, line_color="#00ff88", line_width=2, line_dash="dot", annotation_text=f"TP1 {tp1:.2f} +{tp1_d:.1f} RR 1:{rr1} (50%)")
fig.add_hline(y=tp2, line_color="#00ff88", line_width=2, line_dash="dash", annotation_text=f"TP2 {tp2:.2f} +{tp2_d:.1f} RR 1:{rr2} (30%)")
fig.add_hline(y=tp3, line_color="#00ff88", line_width=3, annotation_text=f"TP3 {tp3:.2f} +{tp3_d:.1f} RR 1:{rr3} (20% RUNNER)")
fig.add_hline(y=live, line_color="white", line_dash="dot", annotation_text=f"LIVE {live:.2f}")
fig.update_layout(height=420, template="plotly_dark", margin=dict(l=0,r=0,t=5,b=0), xaxis_rangeslider_visible=False, yaxis=dict(range=[min(entry,sl,tp1,tp2,tp3,live)-7, max(entry,sl,tp1,tp2,tp3,live)+7]))
st.plotly_chart(fig, use_container_width=True)

col1,col2,col3,col4=st.columns(4)
col1.metric("ENTRY", f"${entry:.2f}", f"{sig} {tf}")
col2.metric(f"TP1 RR 1:{rr1}", f"${tp1:.2f}", f"+${tp1_d:.1f} 50%")
col3.metric(f"TP2 RR 1:{rr2}", f"${tp2:.2f}", f"+${tp2_d:.1f} 30%")
col4.metric(f"TP3 RR 1:{rr3}", f"${tp3:.2f}", f"+${tp3_d:.1f} 20%")

# TradingView with TP1 TP2 TP3
st.write(f"### TRADINGVIEW {tf} — TP1 TP2 TP3 DRAWN")
components.html(f"""
<div id="tv" style="height:600px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
var w=new TradingView.widget({{"autosize":true,"height":600,"symbol":"OANDA:XAUUSD","interval":"{tv_int}","timezone":"Africa/Johannesburg","theme":"dark","container_id":"tv"}});
w.onChartReady(function(){{
 var c=w.chart();
 c.createOrderLine().setText("ENTRY {entry:.2f} {sig}").setPrice({entry}).setLineColor("yellow").setLineWidth(4);
 c.createOrderLine().setText("SL SHORT {sl:.2f} -{sl_d:.1f}").setPrice({sl}).setLineColor("red").setLineWidth(2);
 c.createOrderLine().setText("TP1 {tp1:.2f} +{tp1_d:.1f} RR 1:{rr1} 50%").setPrice({tp1}).setLineColor("#00ff88").setLineWidth(2);
 c.createOrderLine().setText("TP2 {tp2:.2f} +{tp2_d:.1f} RR 1:{rr2} 30%").setPrice({tp2}).setLineColor("#00ff88").setLineWidth(2);
 c.createOrderLine().setText("TP3 RUNNER {tp3:.2f} +{tp3_d:.1f} RR 1:{rr3} 20%").setPrice({tp3}).setLineColor("#00ff88").setLineWidth(3);
 c.createPositionLine().setText("LIVE {live:.2f}").setPrice({live}).setLineColor("white");
}});
</script>
""", height=620)

import urllib.parse
msg=f"{sig} {tf} ENTRY {entry:.2f} LIVE {live:.2f} SL SHORT {sl:.2f} -{sl_d:.1f} TP1 {tp1:.2f} +{tp1_d:.1f} RR1:{rr1} 50% TP2 {tp2:.2f} +{tp2_d:.1f} RR1:{rr2} 30% TP3 {tp3:.2f} +{tp3_d:.1f} RR1:{rr3} 20% | TP1 TP2 TP3 SYSTEM | 0637247675"
st.link_button(f"SEND {sig} TP1 TP2 TP3 -> 0637247675", f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}", type="primary", use_container_width=True)