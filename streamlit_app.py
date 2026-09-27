import streamlit as st, requests, pandas as pd, numpy as np
from datetime import datetime
import plotly.graph_objects as go
import streamlit.components.v1 as components

try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=5000, key="live")
except: pass

st.set_page_config(layout="centered", page_title="Katlego AI LONG RR", page_icon="🤖")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.status-box{background:#151515;border-radius:12px;padding:12px;border:1px solid #333}.tp{background:#00ff88;color:#000;border-radius:8px;padding:6px 10px;font-weight:800}.sl{background:#ff3333;color:#fff;border-radius:8px;padding:6px 10px;font-weight:800}</style>", unsafe_allow_html=True)

if 'trades' not in st.session_state: st.session_state.trades=[]

MY_PHONE="27637247675" # 0637247675

def get_price(s="XAUUSD"):
 try:
  if "XAU" in s: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
  return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}",timeout=4).json()['price'])
 except: return 4259.0

def get_klines(sym, interval="15m"):
 base=get_price(sym)
 try:
  url=f"https://api.binance.com/api/v3/klines?symbol={'PAXGUSDT' if 'XAU' in sym else sym}&interval={interval}&limit=100"
  data=requests.get(url,timeout=6).json()
  if isinstance(data,list) and len(data)>10:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k], errors='coerce')
   return df
 except: pass
 c=[base+np.random.randn()*base*0.0008 for _ in range(100)]
 for i in range(1,100): c[i]=c[i-1]*0.9995+c[i]*0.0005
 return pd.DataFrame({'o':c,'h':[x*1.002 for x in c],'l':[x*0.998 for x in c],'c':c})

def play_sound(): components.html("""<audio autoplay><source src="https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c8b5d0.mp3"></audio>""",height=0)

price=get_price("XAUUSD")
st.markdown(f"<div class='status-box'><b>🚀 LONG TRADE MODE 🟢</b> | XAUUSD ${price:.2f} | Short SL + Long TP 1:3 / 1:5 | WA 0637247675</div>",unsafe_allow_html=True)

st.write("### ⛶ LONG Trades — Short SL / Long TP — RR 1:3 to 1:5")

col1,col2,col3=st.columns(3)
with col1: sym=st.selectbox("Pair",["XAUUSD","BTCUSDT"],0)
with col2: dur=st.selectbox("Hold Time",["30 MIN","1 HOUR ⏰","4 HOUR 🔥","1 DAY 💎"],1)
with col3: rr=st.selectbox("Risk Reward",["1:3 (Safe) 🎯","1:5 (Pro) 🚀","1:2 (Scalp) ⚡"],0)

rr_val=3 if "1:3" in rr else 5 if "1:5" in rr else 2
interval_map={"30 MIN":"15m","1 HOUR ⏰":"15m","4 HOUR 🔥":"1h","1 DAY 💎":"4h"}
interval=interval_map[dur]

df=get_klines(sym, interval)
df['ma_fast']=df['c'].rolling(9).mean(); df['ma_slow']=df['c'].rolling(21).mean()
df['buy_sig']= (df['ma_fast']>df['ma_slow']) & (df['ma_fast'].shift(1)<=df['ma_slow'].shift(1))
df['sell_sig']= (df['ma_fast']<df['ma_slow']) & (df['ma_fast'].shift(1)>=df['ma_slow'].shift(1))

last_price=float(df['c'].iloc[-1]); last_sig="BUY" if df['ma_fast'].iloc[-1]>df['ma_slow'].iloc[-1] else "SELL"

# LONG TRADE: SHORT SL + LONG TP
if "XAU" in sym:
 if dur=="30 MIN": sl_dist=3.0
 elif "1 HOUR" in dur: sl_dist=5.0
 elif "4 HOUR" in dur: sl_dist=8.0
 else: sl_dist=12.0
else:
 sl_dist=last_price*0.003

tp_dist=sl_dist*rr_val # 1:3 => TP 3x bigger than SL!

tp=last_price+tp_dist if last_sig=="BUY" else last_price-tp_dist
sl=last_price-sl_dist if last_sig=="BUY" else last_price+sl_dist

fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df))), open=df['o'], high=df['h'], low=df['l'], close=df['c']))
b_idx=df.index[df['buy_sig']].tolist()[-5:]; s_idx=df.index[df['sell_sig']].tolist()[-5:]
fig.add_trace(go.Scatter(x=b_idx, y=[df['l'].iloc[i]*0.999 for i in b_idx], mode='markers+text', marker=dict(color='#00ff88', size=14, symbol='triangle-up'), text=['Buy']*len(b_idx), textposition='bottom center'))
fig.add_trace(go.Scatter(x=s_idx, y=[df['h'].iloc[i]*1.001 for i in s_idx], mode='markers+text', marker=dict(color='#ff3333', size=14, symbol='triangle-down'), text=['Sell']*len(s_idx), textposition='top center'))
fig.add_hline(y=tp, line_dash="dash", line_color="#00ff88", line_width=2, annotation_text=f"TP LONG +${tp_dist:.1f} (RR 1:{rr_val}) = ${tp:.2f}")
fig.add_hline(y=sl, line_dash="dash", line_color="#ff3333", line_width=2, annotation_text=f"SL SHORT -${sl_dist:.1f} = ${sl:.2f}")
fig.add_hline(y=last_price, line_dash="dot", line_color="yellow", annotation_text=f"ENTRY ${last_price:.2f}")
fig.update_layout(height=500,template="plotly_dark",margin=dict(l=0,r=0,t=10,b=0),xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig,use_container_width=True)

a,b,c,d=st.columns(4)
a.metric(f"{dur} Signal",last_sig)
b.metric("ENTRY",f"${last_price:.2f}")
c.metric("SL SHORT",f"-${sl_dist:.1f}", delta_color="inverse")
d.metric(f"TP LONG 1:{rr_val}",f"+${tp_dist:.1f}")

st.markdown(f"<span class='sl'>🛑 SL SHORT: ${sl:.2f} (-${sl_dist:.1f})</span> <span class='tp'>🎯 TP LONG: ${tp:.2f} (+${tp_dist:.1f}) RR 1:{rr_val}</span>",unsafe_allow_html=True)
st.info(f"💡 LONG TRADE LOGIC: If you risk ${sl_dist:.1f}, you win ${tp_dist:.1f} — Win 1 = cover {rr_val} losses! For {dur}, hold {dur} on Exness MT5.")

if st.button(f"⚡ START LONG {last_sig} {dur} → 0637247675",type="primary",use_container_width=True):
 msg=f"🚀 LONG {sym} {last_sig} {dur} RR 1:{rr_val} @ ${last_price:.2f} SL ${sl:.2f} (-${sl_dist}) TP ${tp:.2f} (+${tp_dist}) — Katlego AI"
 st.session_state.trades.append({"Time":datetime.now().strftime("%H:%M:%S"),"Pair":sym,"Hold":dur,"RR":f"1:{rr_val}","Side":last_sig,"Entry":last_price,"SL":sl,"TP":tp,"Risk":f"-${sl_dist}","Reward":f"+${tp_dist}"})
 play_sound()
 link=f"https://wa.me/{MY_PHONE}?text={requests.utils.quote(msg)}"
 st.link_button(f"📱 SEND LONG TRADE TO 0637247675", link, type="primary", use_container_width=True)
 st.success(f"✅ LONG {dur} {last_sig} SET! SL SHORT -${sl_dist} TP LONG +${tp_dist} RR 1:{rr_val}")
 st.balloons()

if st.session_state.trades:
 st.write("### 📊 LONG Trades History — Short SL Long TP")
 st.dataframe(pd.DataFrame(st.session_state.trades), use_container_width=True)
 total_risk=sum([float(str(x['Risk']).replace('-$','')) for x in st.session_state.trades])
 total_reward=sum([float(str(x['Reward']).replace('+$','')) for x in st.session_state.trades])
 st.metric("Total RR if all win", f"Risk ${total_risk:.1f} → Reward ${total_reward:.1f} = {total_reward/total_risk if total_risk>0 else 0:.1f}x")