def get_btc():
 try:
  u="https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
  r=requests.get(u,timeout=10).json()
  prices=r['prices']
  df=pd.DataFrame(prices,columns=['t','C'])
  df['O']=df['C']; df['H']=df['C']; df['L']=df['C']
  return float(df['C'].iloc[-1]),df
 except:
  return 108500,None