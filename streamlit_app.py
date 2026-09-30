import streamlit as st, requests, pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go
try:
 from streamlit_autorefresh import st_autorefresh
 st_autorefresh(interval=7000, key="final_fix_tv_iframe")
except: pass

st.set_page_config(layout="centered", page_title="XAUUSD BANK + TV", page_icon="🏦")
if 'tp1_hit' not in st.session_state: st.session_state.tp1_hit=False
if 'be_active' not in st.session_state: st.session_state.be_active=False

def get_price():
 try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=4).json()['price'])
 except: return 4150.76

def get_klines(limit=200):
 try:
  data=requests.get(f"https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit={limit}",timeout=5).json()
  if isinstance(data,list) and len(data)>20:
   df=pd.DataFrame(data,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','i'])
   for k in ['o','h','l','c']: df[k]=pd.to_numeric(df[k])
   return df
 except: pass
 base=get_price()
 return pd.DataFrame({'o':[base]*limit,'h':[base*1.001]*limit,'l':[base*0.999]*limit,'c':[base]*limit})

live=get_price()
df=get_klines(200); df_c=df.iloc[:-1].copy()

demands=[]; supplies=[]
for i in range(20, len(df_c)-3):
 body=df_c['c'].iloc[i]-df_c['o'].iloc[i]
 rng=df_c['h'].iloc[i-8:i].max() - df_c['l'].iloc[i-8:i].min()
 if rng==0: continue
 if body > rng*0.6: demands.append({"mid":float((df_c['l'].iloc[i-1]+df_c['l'].iloc[i])/2),"sl":float(df_c['l'].iloc[i-1])})
 if body < -rng*0.6: supplies.append({"mid":float((df_c['h'].iloc[i]+df_c['h'].iloc[i-1])/2),"sl":float(df_c['h'].iloc[i-1])})

df['e9']=df['c'].ewm(9).mean(); df['e21']=df['c'].ewm(21).mean()
e9=float(df['e9'].iloc[-1]); e21=float(df['e21'].iloc[-1])

if demands and e9>e21: sig="BUY"; z=demands[-1]; entry=z['mid']; sl_orig=z['sl']-0.8
else: sig="SELL"; z=supplies[-1] if supplies else {"mid":live+2,"sl":live+3}; entry=z['mid']; sl_orig=z['sl']+0.8

if sig=="BUY": tp1=entry+5; tp2=entry+10; tp3=entry+20; hit=live>=tp1
else: tp1=entry-5; tp2=entry-10; tp3=entry-20; hit=live<=tp1

if hit: st.session_state.be_active=True; st.session_state.tp1_hit=True
sl = entry if st.session_state.be_active else sl_orig
be_text = "🔒 BE SAFE" if st.session_state.be_active else f"SL ${sl_orig:.2f}"

# 1. BUY/SELL LABEL
if sig=="BUY":
 st.markdown(f"<div style='text-align:center;background:#00ff88;color:#000;padding:20px;border-radius:18px'><h1 style='margin:0;font-size:52px'>🟢 BUY</h1><p style='margin:6px 0 0;font-size:18px;font-weight:900'>ENTRY ${entry:.2f} | {be_text}</p></div>", unsafe_allow_html=True)
else:
 st.markdown(f"<div style='text-align:center;background:#ff3333;color:#fff;padding:20px;border-radius:18px'><h1 style='margin:0;font-size:52px'>🔴 SELL</h1><p style='margin:6px 0 0;font-size:18px;font-weight:900'>ENTRY ${entry:.2f} | {be_text}</p></div>", unsafe_allow_html=True)

# 2. TPs
c1,c2,c3=st.columns(3)
c1.metric("TP1 +$5 50%", f"${tp1:.2f}", "✅ BE" if st.session_state.tp1_hit else "TARGET")
c2.metric("TP2 +$10 30%", f"${tp2:.2f}")
c3.metric("TP3 +$20 RUNNER", f"${tp3:.2f}")
st.markdown(f"<p style='text-align:center'>LIVE ${live:.2f} | Dist {abs(live-entry):.1f}</p>", unsafe_allow_html=True)

# 3. TRADINGVIEW - FIXED IFRAME VERSION (100% WORKS)
st.markdown("### 📈 TradingView XAUUSD Live")
components.iframe("https://s.tradingview.com/widgetembed/?frameElementId=tradingview_123&symbol=OANDA%3AXAUUSD&interval=5&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=131722&studies=%5B%5D&theme=dark&style=1&timezone=Africa%2FJohannesburg&withdateranges=1&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en", height=550, scrolling=True)

# 4. BANK CHART
fig=go.Figure()
fig.add_trace(go.Candlestick(x=list(range(len(df_c))), open=df_c['o'], high=df_c['h'], low=df_c['l'], close=df_c['c']))
fig.add_hline(y=entry, line_color="yellow", line_width=4, annotation_text=f"ENTRY {entry:.2f} {sig}")
fig.add_hline(y=sl, line_color="#00b7ff" if st.session_state.be_active else "red", line_width=3, annotation_text=f"{'BE' if st.session_state.be_active else 'SL'} {sl:.2f}")
fig.add_hline(y=tp1, line_color="#00ff88", line_width=2, line_dash="dot", annotation_text=f"TP1 {tp1:.2f}")
fig.add_hline(y=tp2, line_color="#00ff88", line_width=2, line_dash="dash", annotation_text=f"TP2 {tp2:.2f}")
fig.add_hline(y=tp3, line_color="#00ff88", line_width=3, annotation_text=f"TP3 {tp3:.2f}")
fig.add_hline(y=live, line_color="white", line_dash="dot", annotation_text=f"LIVE {live:.2f}")
fig.update_layout(height=520, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

if st.button("🔄 Reset BE"):
 st.session_state.tp1_hit=False; st.session_state.be_active=False; st.rerun()