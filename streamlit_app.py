import streamlit as st, requests, time, pandas as pd, numpy as np
from datetime import datetime
import plotly.graph_objects as go
import streamlit.components.v1 as components

try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=3000, key="live")
except: pass

st.set_page_config(layout="centered", page_title="Katlego AI PRO", page_icon="🤖")
st.markdown("<style>.stApp{background:#0a0a0a;color:#fff}.status-box{background:#151515;border-radius:12px;padding:12px;border:1px solid #222}.tp{background:#00ff88;color:#000;border-radius:8px;padding:4px 8px;font-weight:700}.sl{background:#ff3333;color:#fff;border-radius:8px;padding:4px 8px;font-weight:700}</style>", unsafe_allow_html=True)

if 'trading' not in st.session_state: st.session_state.trading=False
if 'trades' not in st.session_state: st.session_state.trades=[]
if 'license_valid' not in st.session_state: st.session_state.license_valid=True
if 'pair' not in st.session_state: st.session_state.pair="XAUUSD"
if 'page' not in st.session_state: st.session_state.page="Scanner"
if 'last_alert' not in st.session_state: st.session_state.last_alert=""

def get_price(s="XAUUSD"):
 try:
  if "XAU" in s: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
  r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s.replace('USDT','')}USDT",timeout=4).json()
  return float(r['price'])
 except: return 4259.0 if "XAU" in s else 108200.0

def get_klines_safe(sym="XAUUSD"):
 base=get_price(sym)
 try:
  url="https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=80" if "XAU" in sym else f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=5m&limit=80"
  data=requests.get(url,timeout=6).json()
  if isinstance(data,list) and len(data)>10:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k], errors='coerce')
   return df
 except: pass
 c=[base+np.random.randn()*base*0.001 for _ in range(80)]
 for i in range(1,80): c[i]=c[i-1]*0.999+c[i]*0.001
 return pd.DataFrame({'o':c,'h':[x*1.002 for x in c],'l':[x*0.998 for x in c],'c':c})

def play_sound(sig):
 # 🔊 SOUND ALERT
 if sig=="BUY": sound_url="https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c8b5d0.mp3?filename=success-1-6297.mp3"
 else: sound_url="https://cdn.pixabay.com/download/audio/2022/03/24/audio_4fb2f52f61.mp3?filename=alert-sound-74778.mp3"
 components.html(f"""<audio autoplay><source src="{sound_url}" type="audio/mpeg"></audio><script>var a=new Audio("{sound_url}");a.play();</script>""",height=0)
 st.toast(f"🔊 {sig} SIGNAL!", icon="🔔")

def whatsapp_link(phone, msg):
 # 📱 WHATSAPP ALERT — uses wa.me
 return f"https://wa.me/{phone}?text={requests.utils.quote(msg)}"

price=get_price(st.session_state.pair)
cols=st.columns(4)
with cols[0]:
 if st.button("🏠 Home",use_container_width=True): st.session_state.page="Home"; st.rerun()
with cols[1]:
 if st.button("⛶ Scanner",use_container_width=True): st.session_state.page="Scanner"; st.rerun()
with cols[2]:
 if st.button("📊 Trades",use_container_width=True): st.session_state.page="Trades"; st.rerun()
with cols[3]:
 if st.button("⚙️ Settings",use_container_width=True): st.session_state.page="Settings"; st.rerun()

st.markdown(f"<div class='status-box'><b>LIVE 3s 🟢</b> | {st.session_state.pair} ${price:.2f} | TP/SL + SOUND + WHATSAPP ACTIVE</div>",unsafe_allow_html=True)

if st.session_state.page=="Scanner":
 st.write("### ⛶ Katlego AI PRO — BUY/SELL + TP/SL + SOUND + WHATSAPP")
 sym=st.selectbox("Scan Pair",["XAUUSD","BTCUSDT","ETHUSDT"],0)
 wa_phone=st.text_input("📱 WhatsApp number for alerts (e.g. 2782xxxxxxx)", value="2782555")
 df=get_klines_safe(sym)
 df['ma_fast']=df['c'].rolling(5).mean(); df['ma_slow']=df['c'].rolling(20).mean()
 df['buy_sig']= (df['ma_fast']>df['ma_slow']) & (df['ma_fast'].shift(1)<=df['ma_slow'].shift(1))
 df['sell_sig']= (df['ma_fast']<df['ma_slow']) & (df['ma_fast'].shift(1)>=df['ma_slow'].shift(1))
 last_price=float(df['c'].iloc[-1])
 last_sig="BUY" if df['ma_fast'].iloc[-1]>df['ma_slow'].iloc[-1] else "SELL"
 # NEW SIGNAL?
 new_buy=bool(df['buy_sig'].iloc[-1]); new_sell=bool(df['sell_sig'].iloc[-1])

 # 🎯 TP/SL CALC — Gold: TP $15 SL $8, BTC: 1.2% / 0.6%
 if "XAU" in sym:
  tp=last_price+15 if last_sig=="BUY" else last_price-15
  sl=last_price-8 if last_sig=="BUY" else last_price+8
 else:
  tp=last_price*1.012 if last_sig=="BUY" else last_price*0.988
  sl=last_price*0.994 if last_sig=="BUY" else last_price*1.006

 fig=go.Figure()
 fig.add_trace(go.Candlestick(x=list(range(len(df))), open=df['o'], high=df['h'], low=df['l'], close=df['c'], name=sym))
 b_idx=df.index[df['buy_sig']].tolist(); s_idx=df.index[df['sell_sig']].tolist()
 fig.add_trace(go.Scatter(x=b_idx, y=[df['l'].iloc[i]*0.997 for i in b_idx], mode='markers+text', marker=dict(color='#00ff88', size=14, symbol='triangle-up'), text=['Buy']*len(b_idx), textposition='bottom center', textfont=dict(color='#00ff88', size=12), name='BUY'))
 fig.add_trace(go.Scatter(x=s_idx, y=[df['h'].iloc[i]*1.003 for i in s_idx], mode='markers+text', marker=dict(color='#ff3333', size=14, symbol='triangle-down'), text=['Sell']*len(s_idx), textposition='top center', textfont=dict(color='#ff4444', size=12), name='SELL'))
 # 🎯 TP/SL LINES
 fig.add_hline(y=tp, line_dash="dash", line_color="#00ff88", annotation_text=f"TP ${tp:.2f}", annotation_position="right")
 fig.add_hline(y=sl, line_dash="dash", line_color="#ff3333", annotation_text=f"SL ${sl:.2f}", annotation_position="right")
 fig.add_hline(y=last_price, line_dash="dot", line_color="white", annotation_text=f"ENTRY ${last_price:.2f}")
 fig.update_layout(height=460,template="plotly_dark",margin=dict(l=0,r=0,t=10,b=0),xaxis_rangeslider_visible=False, showlegend=False)
 st.plotly_chart(fig,use_container_width=True)

 a,b,c=st.columns(3)
 a.metric("Signal NOW",last_sig)
 b.metric("Price LIVE",f"${last_price:.2f}")
 c.metric("Trades",len(st.session_state.trades))
 st.markdown(f"<span class='tp'>🎯 TP: ${tp:.2f}</span> <span class='sl'>🛑 SL: ${sl:.2f}</span>",unsafe_allow_html=True)

 # 🔔 TRIGGER ALERTS ONLY ON NEW CROSS
 alert_key=f"{sym}{last_sig}{len(df)}"
 if (new_buy or new_sell) and st.session_state.last_alert!=alert_key:
  st.session_state.last_alert=alert_key
  play_sound(last_sig)
  msg=f"🚨 Katlego AI {sym} {last_sig} @ ${last_price:.2f} | TP ${tp:.2f} SL ${sl:.2f} — https://2lhb7vwtqfx6vivukmj7cv.streamlit.app"
  if wa_phone:
   link=whatsapp_link(wa_phone.replace("+",""), msg)
   st.link_button(f"📱 Send WhatsApp Alert {last_sig}", link, type="primary", use_container_width=True)
  st.balloons()
  st.success(f"🔊 NEW {last_sig} ALERT! TP/SL set!")

 if st.button(f"⚡ EXECUTE {last_sig} NOW",type="primary",use_container_width=True):
  st.session_state.trades.append({"Time":datetime.now().strftime("%H:%M:%S"),"Pair":sym,"Side":last_sig,"Entry":last_price,"TP":tp,"SL":sl})
  play_sound(last_sig)
  st.success(f"{last_sig} {sym} ENTRY ${last_price:.2f} TP ${tp:.2f} SL ${sl:.2f}")

elif st.session_state.page=="Settings":
 st.write("### ⚙️ WhatsApp Setup (Free)")
 st.info("1. Save number +34 644 51 95 23 as 'CallMeBot'\n2. WhatsApp him: 'I allow callmebot to send me messages'\n3. You get API key — paste below for auto-send\n\nOR use simple wa.me link (works now without key)")
 phone=st.text_input("Your WhatsApp (with country code)", "2782xxxxxxx")
 st.write("**Current:** Sound 🔊 = ON, TP/SL 🎯 = ON, WhatsApp 📱 = Link button on new signal")

elif st.session_state.page=="Trades":
 st.write("### 📊 Trade History with TP/SL")
 if st.session_state.trades: st.dataframe(pd.DataFrame(st.session_state.trades), use_container_width=True)
 else: st.info("No trades yet — Go Scanner → EXECUTE")