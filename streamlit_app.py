import streamlit as st, requests, time, pandas as pd
from datetime import datetime
st.set_page_config(layout="centered",page_title="Katlego AI",page_icon="🤖")

st.markdown("""
<style>
.stApp { background: #0a0a0a; }
.hero {
  background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.9)), url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=800');
  background-size: cover; background-position: center;
  border-radius: 28px; padding: 18px; height: 420px; position: relative;
  box-shadow: 0 0 30px rgba(255,30,30,0.25); border: 1px solid #222;
}
.status-box { background: #151515; border-radius: 12px; padding: 12px 16px; border: 1px solid #222; }
.dream { text-align:center; color:#999; margin: 18px 0; font-size:15px; }
.brand { text-align:center; margin-top: 260px; }
.brand h2 { color: white; font-weight: 800; margin:0; font-size:24px; }
.brand p { color:#ccc; margin:4px 0; }
.powered {
  text-align:center; background: #111; border:1px solid #ff1a1a; 
  border-radius: 24px; padding:8px 18px; width: fit-content; margin: 0 auto;
  box-shadow: 0 0 15px rgba(255,26,26,0.5); font-size:13px; color:#ccc;
}
.powered span { color:#ff3333; font-weight:700; }
</style>
""", unsafe_allow_html=True)

if 'trading' not in st.session_state: st.session_state.trading=False
if 'trades' not in st.session_state: st.session_state.trades=[]

def get_price():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()['price'])
 except: return 4286.2
price=get_price()

st.markdown(f"""
<div class="status-box">
  <div style="color:white; font-weight:700;">{'Trading Active' if st.session_state.trading else 'Trading Stopped'}</div>
  <div style="color:#888; font-size:12px;">{'Your bot is actively scalping.' if st.session_state.trading else 'Your bot has stopped trading.'}</div>
</div>
<div class="hero">
  <div class="dream">It all starts with a dream.</div>
  <div class="brand">
    <h2>Katlego AI</h2>
    <p>Scalping Bot • ${price:.2f}</p>
  </div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3=st.columns(3)
with c1:
 if st.button("📈 PAIRS", use_container_width=True): st.info("Pairs: XAUUSD, BTCUSD")
with c2:
 if st.button("▶️ START" if not st.session_state.trading else "⏸️ STOP", use_container_width=True, type="primary"):
  st.session_state.trading=not st.session_state.trading; st.rerun()
with c3:
 if st.button("🕒 LOGS", use_container_width=True): st.dataframe(pd.DataFrame(st.session_state.trades) if st.session_state.trades else pd.DataFrame([{"No trades":""}]))

st.markdown("""
<div style="background:#0f0f0f; border:1.5px solid #ff1a1a; border-radius:40px; display:flex; justify-content:space-around; padding:14px 10px; box-shadow:0 0 20px rgba(255,26,26,0.6); margin:22px 0;">
  <div style="text-align:center; color:white;">📉<br><b style="font-size:11px;">PAIRS</b></div>
  <div style="text-align:center; color:white;">▶️<br><b style="font-size:11px;">START</b></div>
  <div style="text-align:center; color:white;">🕒<br><b style="font-size:11px;">LOGS</b></div>
</div>
<div class="powered">Powered by <span>Katlego</span></div>
<div style="margin-top:18px; color:#aaa; font-size:14px;">Robot List</div>
""", unsafe_allow_html=True)

if st.session_state.trading:
 st.markdown(f"""<div style="background:#151515; border-radius:16px; padding:14px; border:1px solid #222; margin-top:12px;"><b style="color:white;">XAUUSD Scalper</b><br><span style="color:#00ff88; font-size:12px;">● LIVE • ${price:.2f} • TP ${price-8:.2f} • SL ${price+10:.2f}</span></div>""", unsafe_allow_html=True)
else:
 st.markdown("""<div style="background:#151515; border-radius:16px; padding:14px; border:1px solid #222; margin-top:12px; opacity:0.6;"><div style="color:white;">XAUUSD Scalper <span style="float:right; color:#666;">Stopped</span></div><div style="color:#666; font-size:12px;">Waiting...</div></div>""", unsafe_allow_html=True)

st.markdown("""<div style="height:80px;"></div><div style="position:fixed; bottom:0; left:0; right:0; background:#0a0a0a; border-top:1px solid #222; display:flex; justify-content:space-around; padding:12px 0 18px 0;"><div style="color:#ff1a1a; text-align:center;">🏠<br>Home</div><div style="color:#666; text-align:center;">🗄️<br>Metatrader</div><div style="color:#666; text-align:center;">⛶<br>Scanner</div><div style="color:#666; text-align:center;">⚙️<br>Settings</div></div>""", unsafe_allow_html=True)

time.sleep(5); st.rerun()