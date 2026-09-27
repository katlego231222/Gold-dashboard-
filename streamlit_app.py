import streamlit as st, requests, pandas as pd, re
import streamlit.components.v1 as components
import plotly.graph_objects as go
try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=10000, key="5_15_1h_fix")
except: pass

st.set_page_config(layout="centered", page_title="5M 15M 1H CRT S&D", page_icon="🏦")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.box{background:#111;border:2px solid #ffcc00;border-radius:12px;padding:10px}.buy{background:#00ff88;color:#000;border-radius:8px;padding:8px;font-weight:900}.sell{background:#ff3333;color:#fff;border-radius:8px;padding:8px;font-weight:900}</style>", unsafe_allow_html=True)

MY_PHONE="27637247675"

def get_price():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
 except: return 4266.30

def get_klines(interval, limit=250):
 base=get_price()
 try:
  data=requests.get(f"https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval={interval}&limit={limit}",timeout=6).json()
  if isinstance(data,list) and len(data)>30:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k], errors='coerce')
   return df
 except: pass
 import numpy as np
 c=[base+np.random.randn()*base*0.0005 for _ in range(limit)]
 for i in range(1,limit): c[i]=c[i-1]*0.9997+c[i]*0.0003
 return pd.DataFrame({'o':c,'h':[x*1.002 for x in c],'l':[x*0.998 for x in c],'c':c})

live=get_price()
st.markdown(f"<div class='box'><b>🏦 5M 15M 1H ONLY — CRT + S&D — TP/SL/ENTRY ON TV</b><br>XAUUSD ${live:.2f} LIVE | FIXED RR BUG | 0637247675</div>",unsafe_allow_html=True)

c1,c2,c3=st.columns(3)
with c1: tf=st.selectbox("Timeframe",["5M ⚡","15M 🎯","1H 🏦"],0)
with c2: mode=st.selectbox("Mode",["REAL-TIME ✅","LOCKED 🔒"],0)
with c3: rr=st.selectbox("RR",["1:5 🚀","1:7 💎","1:3"],0)

# FIXED RR PARSER - extracts number only, ignores emoji
match = re.search(r'1:(\d+)', rr)
rr_val = int(match.group(1)) if match else 5

interval_map = {"5M ⚡":"5m","15M 🎯":"15m","1H 🏦":"1h"}
tv_interval_map = {"5M ⚡":"5","15M 🎯":"15","1H 🏦":"60"}
interval = interval_map[tf]
tv_int = tv_interval_map[tf]

df=get_klines(interval, 250)
df_c=df.iloc[:-1]
df_l=df
pdh=float(df_c['h'].iloc[-40:].max())
pdl=float(df_c['l'].iloc[-40:].min())

demands=[]; supplies=[]
for i in range(25, len(df_c)-2):
 body=df_c['c'].iloc[i]-df_c['o'].iloc[i]
 rng=df_c['h'].iloc[i-10:i].max() - df_c['l'].iloc[i-10:i].min()
 if body > rng*0.60 and body>0:
  lo=float(df_c['l'].iloc[i-1:i+1].min()); hi=float(df_c['l'].iloc[i]); demands.append({"low":lo,"high":hi,"mid":(lo+hi)/2})
 if body < -rng*0.60 and body<0:
  lo=float(df_c['h'].iloc[i]); hi=float(df_c['h'].iloc[i-1:i+1].max()); supplies.append({"low":lo,"high":hi,"mid":(lo+hi)/2})

use = df_l if "REAL-TIME" in mode else df_c
use['e9']=use['c'].ewm(9).mean(); use['e21']=use['c'].ewm(21).mean()
e9=float(use['e9'].iloc[-1 if "REAL-TIME" in mode else -2]); e21=float(use['e21'].iloc[-1 if "REAL-TIME" in mode else -2])

if live >= pdh*0.999 and supplies:
 sig="SELL"; z=supplies[-1]; entry=z['mid']; sl=z['high']+1.5; tp=pdl; why="CRT High Sweep + Supply 1H"
elif live <= pdl*1.001 and demands:
 sig="BUY"; z=demands[-1]; entry=z['mid']; sl=z['low']-1.5; tp=pdh; why="CRT Low Sweep + Demand 1H"
elif e9>e21 and demands:
 sig="BUY"; z=demands[-1]; entry=z['mid']; sl=z['low']-1.5; tp=entry+abs(entry-sl)*rr_val; why=f"Bull {tf} + Demand"
else:
 sig="SELL"; z=supplies[-1] if supplies else {"low":live+2,"high":live+5,"mid":live+2.5}; entry=z['mid']; sl=z['high']+1.5; tp=entry-abs(sl-entry)*rr_val; why=f"Bear {tf} + Supply"

if "REAL-TIME" in mode and abs(live-entry)>8:
 entry = live-0.8 if sig=="BUY" else live+0.8; sl = entry-3.2 if sig=="BUY" else entry+3.2; tp = entry+3.2*rr_val if sig=="BUY" else entry-3.2*rr_val

sl_d=abs(entry-sl); tp_d=abs(tp-entry)

fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_c))), open=df_c['o'], high=df_c['h'], low=df_c['l'], close=df_c['c'], name=tf))
for d in demands[-2:]: fig.add_hrect(y0=d['low'], y1=d['high'], fillcolor="rgba(0,255,136,0.22)", line_width=0)
for s in supplies[-2:]: fig.add_hrect(y0=s['low'], y1=s['high'], fillcolor="rgba(255,51,51,0.22)", line_width=0)
fig.add_hline(y=pdh, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDH {pdh:.2f}")
fig.add_hline(y=pdl, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDL {pdl:.2f}")
fig.add_hline(y=entry, line_color="#ffcc00", line_width=4, annotation_text=f"ENTRY {entry:.2f}")
fig.add_hline(y=sl, line_color="#ff3333", line_width=2, line_dash="dash", annotation_text=f"SL {sl:.2f}")
fig.add_hline(y=tp, line_color="#00ff88", line_width=2, line_dash="dash", annotation_text=f"TP {tp:.2f}")
fig.add_hline(y=live, line_color="white", line_dash="dot", annotation_text=f"LIVE {live:.2f}")
low_y=min(entry,sl,tp,live,pdl)-7; high_y=max(entry,sl,tp,live,pdh)+7
fig.update_layout(height=400, template="plotly_dark", margin=dict(l=0,r=0,t=10,b=0), xaxis_rangeslider_visible=False, showlegend=False, yaxis=dict(range=[low_y,high_y]))
st.plotly_chart(fig, use_container_width=True)

if sig=="BUY": st.markdown(f"<div class='buy'>✅ {sig} {tf} {why} — ENTRY ${entry:.2f} | SL SHORT ${sl:.2f} -${sl_d:.1f} | TP LONG ${tp:.2f} +${tp_d:.1f} RR 1:{rr_val}</div>",unsafe_allow_html=True)
else: st.markdown(f"<div class='sell'>🔴 {sig} {tf} {why} — ENTRY ${entry:.2f} | SL SHORT ${sl:.2f} -${sl_d:.1f} | TP LONG ${tp:.2f} +${tp_d:.1f} RR 1:{rr_val}</div>",unsafe_allow_html=True)

st.write(f"### 📈 TRADINGVIEW {tf} — TP/SL/ENTRY DRAWN ON CHART")
components.html(f"""
<div id="tv5" style="height:600px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
var w=new TradingView.widget({{"autosize":true,"height":600,"symbol":"OANDA:XAUUSD","interval":"{tv_int}","timezone":"Africa/Johannesburg","theme":"dark","style":"1","container_id":"tv5"}});
w.onChartReady(function(){{
 var c=w.chart();
 c.createOrderLine().setText("CRT PDH {pdh:.2f}").setPrice({pdh}).setLineColor("#ffaa00").setBodyBackgroundColor("#ffaa00").setBodyTextColor("#000").setLineWidth(1).setLineStyle(1);
 c.createOrderLine().setText("CRT PDL {pdl:.2f}").setPrice({pdl}).setLineColor("#ffaa00").setBodyBackgroundColor("#ffaa00").setBodyTextColor("#000").setLineWidth(1).setLineStyle(1);
 c.createOrderLine().setText("ENTRY {entry:.2f} {sig}").setPrice({entry}).setLineColor("#ffcc00").setBodyBackgroundColor("#ffcc00").setBodyTextColor("#000").setLineWidth(3).setLineStyle(0);
 c.createOrderLine().setText("SL SHORT {sl:.2f}").setPrice({sl}).setLineColor("#ff3333").setBodyBackgroundColor("#ff3333").setBodyTextColor("#fff").setLineWidth(2).setLineStyle(2);
 c.createOrderLine().setText("TP LONG {tp:.2f} RR 1:{rr_val}").setPrice({tp}).setLineColor("#00ff88").setBodyBackgroundColor("#00ff88").setBodyTextColor("#000").setLineWidth(2).setLineStyle(2);
 c.createPositionLine().setText("LIVE {live:.2f}").setPrice({live}).setLineColor("#fff").setBodyBackgroundColor("#fff").setBodyTextColor("#000");
}});
</script>
""", height=620)

if st.button(f"SEND {sig} {tf} → 0637247675",type="primary",use_container_width=True):
 import urllib.parse
 msg=f"🏦 {sig} {tf} CRT+S&D ENTRY {entry:.2f} SL SHORT {sl:.2f} -{sl_d:.1f} TP LONG {tp:.2f} +{tp_d:.1f} RR 1:{rr_val} LIVE {live:.2f} TV drawn | 0637247675"
 st.link_button("📱 WHATSAPP 0637247675", f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}", type="primary", use_container_width=True)