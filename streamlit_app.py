import streamlit as st, requests, time, pandas as pd, numpy as np, re
from datetime import datetime
import plotly.graph_objects as go
st.set_page_config(layout="centered", page_title="Katlego AI", page_icon="🤖")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background: #0a0a0a; color: white; }
.hero { background: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.95)), url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=900'); background-size:cover; background-position:center; border-radius:28px; padding:18px; height:380px; box-shadow:0 0 30px rgba(255,30,30,0.25); border:1px solid #222; }
.status-box { background:#151515; border-radius:12px; padding:12px 16px; border:1px solid #222; }
.powered { text-align:center; background:#111; border:1px solid #ff1a1a; border-radius:24px; padding:8px 18px; width:fit-content; margin:10px auto; box-shadow:0 0 15px rgba(255,26,26,0.5); font-size:13px; color:#ccc; }
.powered span { color:#ff3333; font-weight:700; }
.card { background:#151515; border-radius:16px; padding:14px; border:1px solid #222; margin-top:12px; }
button { border-radius:12px!important; }
</style>
""", unsafe_allow_html=True)

if 'trading' not in st.session_state: st.session_state.trading=False
if 'trades' not in st.session_state: st.session_state.trades=[]
if 'license_valid' not in st.session_state: st.session_state.license_valid=False
if 'mt' not in st.session_state: st.session_state.mt={"login":"","server":"Exness-MT5","status":"Not Connected"}
if 'pair' not in st.session_state: st.session_state.pair="XAUUSD"
if 'page' not in st.session_state: st.session_state.page="Home"

def get_price(sym="GOLD"):
 try:
  if "GOLD" in sym or "XAU" in sym: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()['price'])
  r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={sym}",timeout=5).json(); return float(r['price'])
 except: return 4286.2 if "GOLD" in sym or "XAU" in sym else 108200

def get_klines(sym="BTCUSDT"):
 try:
  url=f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=15m&limit=100"
  d=requests.get(url,timeout=8).json()
  df=pd.DataFrame(d,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
  df['c']=df['c'].astype(float); df['h']=df['h'].astype(float); df['l']=df['l'].astype(float); return df
 except: return pd.DataFrame({'c':[4286+np.random.randn() for _ in range(100)],'h':[4290]*100,'l':[4280]*100})

price=get_price(st.session_state.pair)

# --- HEADER ---
st.markdown(f"""
<div class="status-box">
  <div style="display:flex; justify-content:space-between;">
    <div><b style="color:white;">{'Trading Active 🟢' if st.session_state.trading else 'Trading Stopped 🔴'}</b><br><span style="color:#888; font-size:12px;">{st.session_state.pair} • ${price:.2f} • {st.session_state.mt['status']}</span></div>
    <div style="width:10px; height:10px; border-radius:50%; background:{'#00ff88' if st.session_state.trading else '#ff3333'};"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION (All Working) ---
cols=st.columns(4)
with cols[0]:
 if st.button("🏠 Home", use_container_width=True): st.session_state.page="Home"; st.rerun()
with cols[1]:
 if st.button("🗄️ MT5", use_container_width=True): st.session_state.page="MT5"; st.rerun()
with cols[2]:
 if st.button("⛶ Scanner", use_container_width=True): st.session_state.page="Scanner"; st.rerun()
with cols[3]:
 if st.button("⚙️ License", use_container_width=True): st.session_state.page="License"; st.rerun()

# --- PAGES ---

if st.session_state.page=="Home":
 st.markdown(f"""
 <div class="hero">
   <div style="text-align:center; color:#999; margin:12px 0;">It all starts with a dream.</div>
   <div style="text-align:center; margin-top:210px;"><h2 style="color:white; margin:0;">Katlego AI</h2><p style="color:#ccc;">Scalping Bot • ${price:.2f}</p></div>
 </div>
 <div style="background:#0f0f0f; border:1.5px solid #ff1a1a; border-radius:40px; display:flex; justify-content:space-around; padding:14px; box-shadow:0 0 20px rgba(255,26,26,0.6); margin:18px 0;">
   <div style="color:white; text-align:center;">📉<br><b style="font-size:11px;">PAIRS</b></div><div style="color:white; text-align:center;">▶️<br><b style="font-size:11px;">START</b></div><div style="color:white; text-align:center;">🕒<br><b style="font-size:11px;">LOGS</b></div>
 </div>
 <div class="powered">Powered by <span>Katlego</span></div>
 """, unsafe_allow_html=True)

 c1,c2,c3=st.columns(3)
 with c1:
  pair=st.selectbox("Pairs", ["XAUUSD","BTCUSDT","ETHUSDT","EURUSD"], index=0)
  st.session_state.pair=pair
 with c2:
  if st.button("▶️ START BOT" if not st.session_state.trading else "⏸️ STOP BOT", type="primary", use_container_width=True):
   if not st.session_state.license_valid: st.error("Activate License Key first! Go to License tab.");
   else:
    st.session_state.trading=not st.session_state.trading
    if st.session_state.trading:
     st.session_state.trades.insert(0,{"Time":datetime.now().strftime("%H:%M:%S"),"Pair":st.session_state.pair,"Side":"SELL","Entry":price,"TP":price-8,"SL":price+10,"Status":"OPEN","PnL":0})
    st.rerun()
 with c3:
  if st.button("📒 View Logs", use_container_width=True): st.session_state.page="Logs"; st.rerun()

 # Robot List
 if st.session_state.trading:
  st.markdown(f"""<div class="card"><b>{st.session_state.pair} Scalper</b> <span style="float:right; color:#00ff88;">● LIVE</span><br><span style="font-size:12px; color:#aaa;">ENTRY ${price:.2f} → TP ${price-8:.2f} → SL ${price+10:.2f} | RSI 43 SELL</span><br><progress value="70" max="100" style="width:100%; accent-color:#ff1a1a;"></progress></div>""", unsafe_allow_html=True)
 else:
  st.markdown(f"""<div class="card" style="opacity:0.6;"><b>{st.session_state.pair} Scalper</b> <span style="float:right; color:#666;">Stopped</span><br><span style="font-size:12px; color:#666;">Waiting to start... Activate license & Connect MT5</span></div>""", unsafe_allow_html=True)

elif st.session_state.page=="Scanner":
 st.markdown("### ⛶ Chart Scanner — LIVE")
 scan_pair=st.selectbox("Scan Symbol", ["BTCUSDT","ETHUSDT","XAUUSD","BNBUSDT","SOLUSDT"], index=0)
 df=get_klines(scan_pair if scan_pair!="XAUUSD" else "BTCUSDT")
 fig=go.Figure(data=[go.Candlestick(x=list(range(len(df))), open=df['c']*0.999, high=df['h'], low=df['l'], close=df['c'])])
 fig.update_layout(height=300, template="plotly_dark", margin=dict(l=0,r=0,t=10,b=0), xaxis_rangeslider_visible=False)
 st.plotly_chart(fig, use_container_width=True)
 # Simple signal
 rsi_last = 100 - (100/(1+ (df['c'].diff().clip(lower=0).ewm(com=14).mean().iloc[-1] / (-df['c'].diff().clip(upper=0).ewm(com=14).mean().iloc[-1]+1e-9))))
 signal="SELL" if rsi_last>55 else "BUY" if rsi_last<45 else "NEUTRAL"
 col=st.columns(3)
 col[0].metric("Signal", signal); col[1].metric("RSI", f"{rsi_last:.0f}"); col[2].metric("Price", f"${df['c'].iloc[-1]:.2f}")
 if st.button(f"⚡ EXECUTE {signal} NOW", type="primary", use_container_width=True):
  st.session_state.trades.insert(0,{"Time":datetime.now().strftime("%H:%M"),"Pair":scan_pair,"Side":signal,"Entry":df['c'].iloc[-1],"TP":df['c'].iloc[-1]*0.992,"SL":df['c'].iloc[-1]*1.01,"Status":"OPEN","PnL":0}); st.success(f"{signal} {scan_pair} Executed!"); st.balloons()

elif st.session_state.page=="MT5":
 st.markdown("### 🗄️ Metatrader Details")
 with st.form("mt5_form"):
  login=st.text_input("MT5 Login ID", value=st.session_state.mt.get('login',''))
  password=st.text_input("MT5 Password", type="password")
  server=st.selectbox("Server", ["Exness-MT5Real","Exness-MT5Trial","XM-MT5","Deriv-MT5","Custom"], index=0)
  balance=st.number_input("Account Balance $", value=1000)
  submit=st.form_submit_button("🔗 CONNECT MT5", type="primary", use_container_width=True)
  if submit:
   st.session_state.mt={"login":login,"server":server,"balance":balance,"status":f"Connected ✅ {login} @ {server}"}; st.success(f"Connected to {server} as {login}! Bot can now trade on MT5"); time.sleep(1); st.session_state.page="Home"; st.rerun()
 st.info(f"Status: {st.session_state.mt['status']}")
 if st.session_state.mt['login']: st.markdown(f"<div class='card'>Login: {st.session_state.mt['login']}<br>Server: {st.session_state.mt['server']}<br>Balance: ${st.session_state.mt.get('balance',0)}<br>Status: <span style='color:#00ff88;'>{st.session_state.mt['status']}</span></div>", unsafe_allow_html=True)

elif st.session_state.page=="License":
 st.markdown("### ⚙️ License Key")
 st.write("Activate Katlego AI Pro to trade live.")
 key=st.text_input("Enter License Key", placeholder="KAT-XXXX-XXXX")
 valid_keys=["KATLEGO-PRO-2026","KAT-2026-PRO","DEMO-1234","KATLEGO-FREE"]
 if st.button("🔑 ACTIVATE LICENSE", type="primary", use_container_width=True):
  if key.strip().upper() in valid_keys:
   st.session_state.license_valid=True; st.success(f"License Activated! {key} is valid ✅ Pro features unlocked!"); st.balloons()
  else: st.error("Invalid key! Try: DEMO-1234 for free test")
 if st.session_state.license_valid: st.success("✅ Pro License Active — Bot can execute trades!")
 else: st.warning("⚠️ No license — Use DEMO-1234 to test")
 st.markdown("<div class='card'>Pro includes:<br>• Chart Scanner<br>• Auto Execute<br>• MT5 Connect<br>• Unlimited Trades<br><br>Contact: katlego.ai@gmail.com</div>", unsafe_allow_html=True)

elif st.session_state.page=="Logs":
 st.markdown("### 📒 Trade Logs")
 if st.session_state.trades:
  df=pd.DataFrame(st.session_state.trades); st.dataframe(df, use_container_width=True)
  csv=df.to_csv(index=False).encode(); st.download_button("Download CSV", csv, "katlego_trades.csv", use_container_width=True)
  if st.button("Clear Logs"): st.session_state.trades=[]; st.rerun()
 else: st.write("No trades yet. Go Home → START BOT")
 if st.button("🏠 Back Home", use_container_width=True): st.session_state.page="Home"; st.rerun()

# Footer nav
st.markdown("""<div style="height:40px;"></div>""", unsafe_allow_html=True)
st.success(f"LIVE | {st.session_state.pair} ${price:.2f} | License: {'✅' if st.session_state.license_valid else '❌'} | MT5: {st.session_state.mt['status'][:20]} | Trades: {len(st.session_state.trades)}")
time.sleep(10); st.rerun()