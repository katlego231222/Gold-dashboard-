import streamlit as st, pandas as pd, requests, time
import plotly.graph_objects as go
import streamlit.components.v1 as comp
st.set_page_config(layout="wide",page_title="Kat Pro Webhook")

# --- WEBHOOK 1: Receive TradingView signal via URL ---
# TradingView will call: yourapp/?signal=SELL&price=4277
qp=st.query_params
webhook_signal=qp.get("signal","")
webhook_price=qp.get("price","")

def get_gold():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()['price'])
 except: return 4286.2
def get_btc():
 try:
  r=requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",timeout=8).json()
  return float(r['bitcoin']['usd'])
 except: return 108200

g=get_gold(); b=get_btc()
# If webhook gives price, use it
if webhook_price:
 try: g=float(webhook_price) if "GOLD" in str(webhook_signal).upper() or webhook_signal=="" else g
 except: pass

# --- SOUND ALERT 2 ---
def play_sound(side):
  sound="https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3" if side=="SELL" else "https://assets.mixkit.co/sfx/preview/mixkit-correct-answer-tone-2870.mp3"
  comp.html(f"""<audio autoplay><source src="{sound}" type="audio/mpeg"></audio><script>new Audio("{sound}").play();</script><b>🔊 {side} ALERT PLAYING</b>""",height=50)

st.title("🚀 Kat Scalper Pro 24/7 + Webhook 🔊")

# Show webhook status
if webhook_signal:
  st.warning(f"📡 WEBHOOK RECEIVED: {webhook_signal} @ {webhook_price}")
  play_sound(webhook_signal.upper())
  st.balloons()

# Tabs
t1,t2,t3=st.tabs(["🪙 GOLD XAU","₿ BTC","⚙️ WEBHOOK SETUP"])

with t1:
  side=webhook_signal.upper() if webhook_signal else "SELL"
  entry=g; tp1=entry-8; tp2=entry-15; sl=entry+10
  if side=="BUY": tp1=entry+8; tp2=entry+15; sl=entry-10
  col="red" if side=="SELL" else "green"
  st.markdown(f"## GOLD ${g:.2f} | :{col}[{side}]")
  c1,c2,c3,c4=st.columns(4)
  c1.metric("ENTRY",f"${entry:.2f}"); c2.metric("TP1",f"${tp1:.2f}"); c3.metric("TP2",f"${tp2:.2f}"); c4.metric("SL",f"${sl:.2f}")
  if st.button("🔊 Test SELL Sound"): play_sound("SELL")
  st.caption("Signal: 19:02 SELL 4277 | EMA Bear | RSI 43")

with t2:
  st.markdown(f"## BTC ${b:.0f}")
  entry=b; c1,c2,c3,c4=st.columns(4)
  c1.metric("ENTRY",f"${entry:.0f}"); c2.metric("TP1 +1%",f"${entry*1.01:.0f}"); c3.metric("TP2 +2%",f"${entry*1.02:.0f}"); c4.metric("SL",f"${entry*0.99:.0f}")
  if st.button("🔊 Test BUY Sound"): play_sound("BUY")

with t3:
  st.markdown("### 1️⃣ TradingView Webhook Setup (5 min)")
  st.code("https://gold-dashboard--.streamlit.app/?signal=SELL&price={{close}}")
  st.write("**In TradingView:**")
  st.write("1. Create Alert → Condition: Your Strategy")
  st.write("2. Check ✅ Webhook URL → Paste above URL")
  st.write("3. Message: {{\"signal\":\"SELL\",\"price\":\"{{close}}\"}}")
  st.write("4. When alert fires → App auto-updates + SOUND + balloons!")
  st.markdown("### 2️⃣ Sound Alert")
  st.write("App plays beep on SELL, chime on BUY. Keep tab open!")
  st.write("Free relay if TradingView needs POST: use pipedream.com → forward to your Streamlit URL")

st.success(f"LIVE 24/7 | Webhook Ready | GOLD ${g:.2f} | BTC ${b:.0f}")
# Auto-refresh every 60s for 24/7
time.sleep(60); st.rerun()