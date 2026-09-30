import streamlit as st, requests, pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go
try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=7000, key="bank_sd_auto_be_final")
except: pass

st.set_page_config(layout="centered", page_title="BANK S&D AUTO BE FINAL", page_icon="🏦")
if 'alert_fired' not in st.session_state: st.session_state.alert_fired=False
if 'last_entry' not in st.session_state: st.session_state.last_entry=0
if 'tp1_hit' not in st.session_state: st.session_state.tp1_hit=False
if 'be_active' not in st.session_state: st.session_state.be_active=False

MY_PHONE="27637247675"
TP1_D,TP2_D,TP3_D=5.0,10.0,20.0

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
st.markdown(f"<h2 style='text-align:center'>🏦 BANK S&D AUTO BE FINAL v1.0<br>XAUUSD ${live:.2f} LIVE</h2>", unsafe_allow_html=True)

tf = st.selectbox("Timeframe",["5M","15M","1H"],1)
mode = st.selectbox("Mode",["REAL-TIME","LOCKED"],0)
interval = {"5M":"5m","15M":"15m","1H":"1h"}[tf]
tv_int = {"5M":"5","15M":"15","1H":"60"}[tf]

df=get_klines(interval); df_c=df.iloc[:-1]

# BANK S&D IMBALANCE STRATEGY
demands=[]; supplies=[]
for i in range(20, len(df_c)-3):
 body=df_c['c'].iloc[i]-df_c['o'].iloc[i]
 rng=df_c['h'].iloc[i-8:i].max() - df_c['l'].iloc[i-8:i].min()
 if body > rng*0.6: demands.append({"low":float(df_c['l'].iloc[i-1]),"high":float(df_c['l'].iloc[i]),"mid":float(df_c['l'].iloc[i-1]+df_c['l'].iloc[i])/2})
 if body < -rng*0.6: supplies.append({"low":float(df_c['h'].iloc[i]),"high":float(df_c['h'].iloc[i-1]),"mid":float(df_c['h'].iloc[i]+df_c['h'].iloc[i-1])/2})

use=df if mode=="REAL-TIME" else df_c
use['e9']=use['c'].ewm(9).mean(); use['e21']=use['c'].ewm(21).mean()
e9=float(use['e9'].iloc[-1]); e21=float(use['e21'].iloc[-1])

if demands and e9>e21:
 sig="BUY"; z=demands[-1]; entry=z['mid']; sl_orig=z['low']-0.8
else:
 sig="SELL"; z=supplies[-1] if supplies else {"mid":live+2,"low":live+1,"high":live+3}; entry=z['mid']; sl_orig=z['high']+0.8

if abs(entry-sl_orig)>4: sl_orig=entry-3 if sig=="BUY" else entry+3
if mode=="REAL-TIME" and abs(live-entry)>6:
 entry=live-0.5 if sig=="BUY" else live+0.5
 sl_orig=entry-2.8 if sig=="BUY" else entry+2.8

if abs(st.session_state.last_entry-entry)>1.0:
 st.session_state.tp1_hit=False; st.session_state.be_active=False
 st.session_state.alert_fired=False; st.session_state.last_entry=entry

sl_d_orig=abs(entry-sl_orig)
if sig=="BUY":
 tp1=entry+TP1_D; tp2=entry+TP2_D; tp3=entry+TP3_D
 tp1_hit_now=live>=tp1
else:
 tp1=entry-TP1_D; tp2=entry-TP2_D; tp3=entry-TP3_D
 tp1_hit_now=live<=tp1

if tp1_hit_now and not st.session_state.tp1_hit:
 st.session_state.tp1_hit=True; st.session_state.be_active=True; st.balloons()

sl = entry if st.session_state.be_active else sl_orig
sl_text = f"SL MOVED TO BE {sl:.2f} 🔒 SAFE" if st.session_state.be_active else f"SL SHORT {sl:.2f} -{sl_d_orig:.1f}"
sl_color = "blue" if st.session_state.be_active else "red"

dist=abs(live-entry)
if dist<=0.7 and not st.session_state.alert_fired:
 st.session_state.alert_fired=True
 components.html(f"<audio autoplay><source src='https://cdn.pixabay.com/download/audio/2022/03/24/audio_1a7dfe20f3.mp3'></audio><script>alert('ENTRY HIT! {sig} {entry:.2f}');</script>", height=0)

if st.session_state.be_active:
 st.success(f"🔒 AUTO BE ACTIVE! TP1 +$5 HIT! SL @ BE ${entry:.2f} RISK FREE → TP2 +$10 TP3 +$20 running")
elif st.session_state.tp1_hit:
 st.success(f"✅ TP1 +$5 HIT! BE ON")
else:
 st.info(f"BANK S&D: ENTRY ${entry:.2f} {sig} | LIVE ${live:.2f} Dist ${dist:.1f} | SL -${sl_d_orig:.1f} | TP1 +$5 TP2 +$10 TP3 +$20 | Auto BE after TP1")

cA,cB=st.columns(2)
if st.button("Reset All Alerts"):
 for k in ['alert_fired','tp1_hit','be_active']: st.session_state[k]=False
 st.rerun()
if st.button("Simulate TP1 Hit (test BE)"): st.session_state.tp1_hit=True; st.session_state.be_active=True; st.rerun()

fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_c))), open=df_c['o'], high=df_c['h'], low=df_c['l'], close=df_c['c']))
fig.add_hline(y=entry, line_color="yellow", line_width=4, annotation_text=f"ENTRY {entry:.2f}")
fig.add_hline(y=sl_orig, line_color="red", line_width=1, line_dash="dot", annotation_text=f"ORIG SL {sl_orig:.2f}")
fig.add_hline(y=sl, line_color=sl_color, line_width=3, annotation_text=sl_text)
fig.add_hline(y=tp1, line_color="#00ff88" if not st.session_state.tp1_hit else "gray", line_width=2, line_dash="dot", annotation_text=f"TP1 {tp1:.2f} +$5 50% {'✅ HIT' if st.session_state.tp1_hit else ''}")
fig.add_hline(y=tp2, line_color="#00ff88", line_width=2, line_dash="dash", annotation_text=f"TP2 {tp2:.2f} +$10 30%")
fig.add_hline(y=tp3, line_color="#00ff88", line_width=3, annotation_text=f"TP3 {tp3:.2f} +$20 20% RUNNER")
fig.add_hline(y=live, line_color="white", line_dash="dot", annotation_text=f"LIVE {live:.2f}")
fig.update_layout(height=460, template="plotly_dark", margin=dict(l=0,r=0,t=5,b=0), xaxis_rangeslider_visible=False, yaxis=dict(range=[min(entry,sl_orig,tp1,tp2,tp3,live)-8, max(entry,sl_orig,tp1,tp2,tp3,live)+8]))
st.plotly_chart(fig, use_container_width=True)

c1,c2,c3,c4=st.columns(4)
c1.metric("ENTRY", f"${entry:.2f}", sig)
c2.metric("TP1 +$5", f"${tp1:.2f}", "✅ BE" if st.session_state.tp1_hit else "50%")
c3.metric("TP2 +$10", f"${tp2:.2f}", "30%")
c4.metric("TP3 +$20", f"${tp3:.2f}", "20% RUNNER")

components.html(f"""
<div id="tv" style="height:600px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
var w=new TradingView.widget({{"autosize":true,"height":600,"symbol":"OANDA:XAUUSD","interval":"{tv_int}","timezone":"Africa/Johannesburg","theme":"dark","container_id":"tv"}});
w.onChartReady(function(){{
 var c=w.chart();
 c.createOrderLine().setText("ENTRY {entry:.2f}").setPrice({entry}).setLineColor("yellow").setLineWidth(4);
 c.createOrderLine().setText("{sl_text}").setPrice({sl}).setLineColor("{sl_color}").setLineWidth(3);
 c.createOrderLine().setText("TP1 +$5 {tp1:.2f}").setPrice({tp1}).setLineColor("#00ff88").setLineWidth(2);
 c.createOrderLine().setText("TP2 +$10 {tp2:.2f}").setPrice({tp2}).setLineColor("#00ff88").setLineWidth(2);
 c.createOrderLine().setText("TP3 +$20 {tp3:.2f}").setPrice({tp3}).setLineColor("#00ff88").setLineWidth(3);
 c.createPositionLine().setText("LIVE {live:.2f}").setPrice({live}).setLineColor("white");
}});
</script>
""", height=620)

import urllib.parse
be_msg = "BE ACTIVE SL=ENTRY RISK FREE" if st.session_state.be_active else f"SL {sl_orig:.2f} -{sl_d_orig:.1f}"
msg=f"🏦 BANK S&D FINAL {sig} {tf} ENTRY {entry:.2f} {be_msg} TP1 {tp1:.2f} +$5 50% TP2 {tp2:.2f} +$10 30% TP3 {tp3:.2f} +$20 20% LIVE {live:.2f} | 0637247675"
st.link_button(f"SEND {sig} BANK FINAL -> 0637247675", f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}", type="primary", use_container_width=True)
st.caption("🏦 STRATEGY: Supply/Demand Imbalance + EMA 9/21 Trend + Fixed $5 $10 $20 + AUTO BE after TP1 | FINAL LOCKED v1.0")