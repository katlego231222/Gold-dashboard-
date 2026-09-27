import streamlit as st, requests, pandas as pd, re
import streamlit.components.v1 as components
import plotly.graph_objects as go
try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=10000, key="long_tp_short_sl")
except: pass

st.set_page_config(layout="centered", page_title="LONG TP SHORT SL", page_icon="💎")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.box{background:#111;border:3px solid #00ff88;border-radius:14px;padding:12px}.entry{background:#ffcc00;color:#000;border-radius:8px;padding:10px 14px;font-weight:900;font-size:18px}.sl{background:#ff3333;color:#fff;border-radius:8px;padding:10px 14px;font-weight:900}.tp{background:#00ff88;color:#000;border-radius:8px;padding:10px 14px;font-weight:900;font-size:18px}</style>", unsafe_allow_html=True)

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

st.markdown(f"""
<div class='box'>
<b>💎 LONG TP + ENTRY + SHORT SL — 5M 15M 1H ONLY</b><br>
XAUUSD ${live:.2f} LIVE | SHORT SL = 2-3$ tight | LONG TP = 15-25$ big | 0637247675
</div>
""",unsafe_allow_html=True)

c1,c2,c3=st.columns(3)
with c1: tf=st.selectbox("Timeframe",["5M ⚡ Sniper","15M 🎯 Accurate","1H 🏦 Swing"],1)
with c2: mode=st.selectbox("Mode",["REAL-TIME ✅ Match MT5","LOCKED 🔒 No Repaint"],0)
with c3: rr=st.selectbox("RR",["1:7 💎 LONG TP","1:5 🚀 LONG TP","1:3"],0)

m = re.search(r'1:(\d+)', rr)
rr_val = int(m.group(1)) if m else 7

interval_map={"5M ⚡ Sniper":"5m","15M 🎯 Accurate":"15m","1H 🏦 Swing":"1h"}
tv_map={"5M ⚡ Sniper":"5","15M 🎯 Accurate":"15","1H 🏦 Swing":"60"}
interval=interval_map[tf]
tv_int=tv_map[tf]

df=get_klines(interval, 250)
df_c=df.iloc[:-1]

# CRT PDH/PDL
pdh=float(df_c['h'].iloc[-50:].max())
pdl=float(df_c['l'].iloc[-50:].min())

# SUPPLY & DEMAND - tight zones for SHORT SL
demands=[]; supplies=[]
for i in range(25, len(df_c)-2):
 body=df_c['c'].iloc[i]-df_c['o'].iloc[i]
 rng=df_c['h'].iloc[i-10:i].max() - df_c['l'].iloc[i-10:i].min()
 if body > rng*0.65 and body>0:
  lo=float(df_c['l'].iloc[i-1:i+1].min()); hi=float(df_c['l'].iloc[i]); demands.append({"low":lo,"high":hi,"mid":(lo+hi)/2,"height":hi-lo})
 if body < -rng*0.65 and body<0:
  lo=float(df_c['h'].iloc[i]); hi=float(df_c['h'].iloc[i-1:i+1].max()); supplies.append({"low":lo,"high":hi,"mid":(lo+hi)/2,"height":hi-lo})

# Filter smallest zones = SHORT SL
demands = sorted(demands, key=lambda x: x['height'])[-3:] if demands else []
supplies = sorted(supplies, key=lambda x: x['height'])[-3:] if supplies else []

use = df if "REAL-TIME" in mode else df_c
use['e9']=use['c'].ewm(9).mean(); use['e21']=use['c'].ewm(21).mean()
e9=float(use['e9'].iloc[-1 if "REAL-TIME" in mode else -2]); e21=float(use['e21'].iloc[-1 if "REAL-TIME" in mode else -2])

# LONG TP + ENTRY + SHORT SL LOGIC
if live <= pdl*1.001 and demands:
 sig="BUY"; z=min(demands, key=lambda x: x['height']); entry=z['mid']; sl=z['low']-0.8; tp=entry+abs(entry-sl)*rr_val; why="CRT Low + Demand — SHORT SL"
elif live >= pdh*0.999 and supplies:
 sig="SELL"; z=min(supplies, key=lambda x: x['height']); entry=z['mid']; sl=z['high']+0.8; tp=entry-abs(entry-sl)*rr_val; why="CRT High + Supply — SHORT SL"
elif e9>e21 and demands:
 sig="BUY"; z=min(demands, key=lambda x: x['height']); entry=z['mid']; sl=z['low']-0.8; tp=entry+abs(entry-sl)*rr_val; why=f"BUY {tf} — SHORT SL"
else:
 sig="SELL"; z=min(supplies, key=lambda x: x['height']) if supplies else {"low":live+2,"high":live+4,"mid":live+2.5,"height":2}; entry=z['mid']; sl=z['high']+0.8; tp=entry-abs(entry-sl)*rr_val; why=f"SELL {tf} — SHORT SL"

# Force SHORT SL if too big
if abs(entry-sl) > 4.5:
 if sig=="BUY": sl=entry-3.0
 else: sl=entry+3.0
 tp = entry + 3.0*rr_val if sig=="BUY" else entry - 3.0*rr_val

# REAL-TIME nudge
if "REAL-TIME" in mode and abs(live-entry) > 7:
 entry = live-0.5 if sig=="BUY" else live+0.5
 sl = entry-2.8 if sig=="BUY" else entry+2.8
 tp = entry+2.8*rr_val if sig=="BUY" else entry-2.8*rr_val

sl_d=abs(entry-sl); tp_d=abs(tp-entry)

# PLOTLY - SHORT SL LONG TP VISUAL
fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_c))), open=df_c['o'], high=df_c['h'], low=df_c['l'], close=df_c['c'], name=tf))
for d in demands: fig.add_hrect(y0=d['low'], y1=d['high'], fillcolor="rgba(0,255,136,0.25)", line_width=0)
for s in supplies: fig.add_hrect(y0=s['low'], y1=s['high'], fillcolor="rgba(255,51,51,0.25)", line_width=0)
fig.add_hline(y=entry, line_color="#ffcc00", line_width=4, annotation_text=f"ENTRY {entry:.2f}")
fig.add_hline(y=sl, line_color="#ff3333", line_width=3, line_dash="dash", annotation_text=f"SL SHORT {sl:.2f} -${sl_d:.1f}")
fig.add_hline(y=tp, line_color="#00ff88", line_width=3, line_dash="dash", annotation_text=f"TP LONG {tp:.2f} +${tp_d:.1f} RR 1:{rr_val}")
fig.add_hline(y=live, line_color="white", line_dash="dot", annotation_text=f"LIVE {live:.2f}")
fig.add_hline(y=pdh, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDH {pdh:.2f}")
fig.add_hline(y=pdl, line_dash="dot", line_color="#ffaa00", annotation_text=f"PDL {pdl:.2f}")
fig.update_layout(height=420, template="plotly_dark", margin=dict(l=0,r=0,t=10,b=0), xaxis_rangeslider_visible=False, showlegend=False, yaxis=dict(range=[min(entry,sl,tp,live,pdl)-8, max(entry,sl,tp,live,pdh)+8]))
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
<div style='display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;'>
<div class='entry'>ENTRY ${entry:.2f}</div>
<div class='sl'>SL SHORT ${sl:.2f} -${sl_d:.1f} TIGHT</div>
<div class='tp'>TP LONG ${tp:.2f} +${tp_d:.1f} RR 1:{rr_val} BIG</div>
</div>
""",unsafe_allow_html=True)

if sig=="BUY":
 st.markdown(f"<div class='tp'>✅ {sig} {tf} {why} — ENTRY ${entry:.2f} | SL SHORT -${sl_d:.1f} | TP LONG +${tp_d:.1f} RR 1:{rr_val}</div>",unsafe_allow_html=True)
else:
 st.markdown(f"<div class='sl'>🔴 {sig} {tf} {why} — ENTRY ${entry:.2f} | SL SHORT -${sl_d:.1f} | TP LONG +${tp_d:.1f} RR 1:{rr_val}</div>",unsafe_allow_html=True)

# TRADINGVIEW WITH LONG TP SHORT SL DRAWN
st.write(f"### 📈 TRADINGVIEW {tf} — LONG TP + ENTRY + SHORT SL DRAWN")
components.html(f"""
<div id="tv_long" style="height:620px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
var w=new TradingView.widget({{"autosize":true,"height":620,"symbol":"OANDA:XAUUSD","interval":"{tv_int}","timezone":"Africa/Johannesburg","theme":"dark","style":"1","container_id":"tv_long"}});
w.onChartReady(function(){{
 var c=w.chart();
 c.createOrderLine().setText("ENTRY {entry:.2f} {sig}").setPrice({entry}).setLineColor("#ffcc00").setBodyBackgroundColor("#ffcc00").setBodyTextColor("#000").setLineWidth(4).setLineStyle(0);
 c.createOrderLine().setText("SL SHORT {sl:.2f} -${sl_d:.1f} TIGHT STOP").setPrice({sl}).setLineColor("#ff3333").setBodyBackgroundColor("#ff3333").setBodyTextColor("#fff").setLineWidth(3).setLineStyle(2);
 c.createOrderLine().setText("TP LONG {tp:.2f} +${tp_d:.1f} RR 1:{rr_val} BIG TARGET").setPrice({tp}).setLineColor("#00ff88").setBodyBackgroundColor("#00ff88").setBodyTextColor("#000").setLineWidth(3).setLineStyle(2);
 c.createPositionLine().setText("LIVE {live:.2f}").setPrice({live}).setLineColor("#fff").setBodyBackgroundColor("#fff").setBodyTextColor("#000");
}});
</script>
""", height=640)

st.caption(f"💎 SHORT SL = Only ${sl_d:.1f} risk | LONG TP = ${tp_d:.1f} profit | ENTRY = 50% of S&D zone | RR 1:{rr_val} | {tf}")

if st.button(f"💎 SEND LONG TP SHORT SL {sig} {tf} → 0637247675",type="primary",use_container_width=True):
 import urllib.parse
 msg=f"💎 LONG TP SHORT SL {sig} {tf} ENTRY {entry:.2f} SL SHORT {sl:.2f} -{sl_d:.1f} TIGHT TP LONG {tp:.2f} +{tp_d:.1f} RR 1:{rr_val} BIG | LIVE {live:.2f} | TV levels drawn | 0637247675"
 st.link_button("📱 SEND TO 0637247675", f"https://wa.me/{MY_PHONE}?text={urllib.parse.quote(msg)}", type="primary", use_container_width=True)
 st.balloons()