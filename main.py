import os
import ccxt
import pandas as pd
import requests

PUSHBULLET_TOKEN = os.getenv('PUSHBULLET_TOKEN')

def send_push(title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'}
    data = {'type': 'note', 'title': title, 'body': body}
    requests.post(url, headers=headers, json=data)

def find_precise_ob(df):
    # শক্তিশালী OB খোঁজা (লাল ক্যান্ডেলের পর শক্তিশালী বুলিশ মুভ)
    for i in range(len(df)-40, len(df)-5):
        if df['close'].iloc[i] < df['open'].iloc[i]: # লাল ক্যান্ডেল
            if df['close'].iloc[i+1] > df['high'].iloc[i] and df['close'].iloc[i+3] > df['high'].iloc[i]:
                return {'low': df['low'].iloc[i], 'high': df['high'].iloc[i]}
    return None

def analyze_market(symbol, tf):
    try:
        exchange = ccxt.mexc()
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        last_price = df['close'].iloc[-1]
        ob = find_precise_ob(df)
        
        if ob:
            # প্রাইস যখন ঠিক জোনের সীমানায় (০.০২% গ্যাপ)
            if last_price <= (ob['high'] * 1.0002) and last_price >= (ob['low'] * 0.9998):
                send_push(f"🎯 OB TOUCH: {symbol} ({tf})", 
                          f"Price is EXACTLY inside your Bullish OB!\n"
                          f"OB Zone: {ob['low']} - {ob['high']}\n"
                          f"Current Price: {last_price}\n"
                          f"Check Chart Now!")

    except Exception as e:
        print(f"Error on {tf}: {e}")

if __name__ == "__main__":
    # আপনার রিকোয়েস্ট অনুযায়ী সবগুলো টাইমফ্রেম
    timeframes = ['5m', '10m', '15m', '30m', '1h', '1d']
    for tf in timeframes:
        analyze_market('BTC/USDT', tf)
