@st.cache_data(ttl=60)
def get_btc_fast():
    try:
        b = yf.download("BTC-USD", period="1d", interval="15m", progress=False, timeout=10)
        return float(b['Close'].iloc[-1]), b
    except:
        return 108500.0, None
btc_price, btc_data = get_btc_fast()