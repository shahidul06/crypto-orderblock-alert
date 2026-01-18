import os
import ccxt
import pandas as pd
import requests

PUSHBULLET_TOKEN = os.getenv('PUSHBULLET_TOKEN')

def send_push(title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'}
    data = {'type': 'note', 'title': title, 'body': body}
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Error sending push: {e}")

def find_order_blocks(df, tf):
    obs = []
    # গত ৫০টি ক্যান্ডেলের মধ্যে OB খোঁজা
    for i in range(2, 48):
        # Bullish OB লজিক: রেড ক্যান্ডেলের পর শক্তিশালী বুলিশ মুভ যা ওই ক্যান্ডেলের হাই ব্রেক করে
        if df['close'].iloc[i] < df['open'].iloc[i]: 
            if df['close'].iloc[i+1] > df['high'].iloc[i] and df['volume'].iloc[i+1] > df['volume'].iloc[i]:
                obs.append({'price': df['low'].iloc[i], 'type': f'{tf} Bullish OB'})
    return obs

def analyze_market(symbol, tf):
    try:
        exchange = ccxt.mexc()
        # নির্দিষ্ট টাইমফ্রেমের ১০০টি ক্যান্ডেল ডাটা সংগ্রহ
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        last_price = df['close'].iloc[-1]
        order_blocks = find_order_blocks(df, tf)
        
        for ob in order_blocks:
            # প্রাইস যদি ওই টাইমফ্রেমের ওবি জোনের ০.১% এরিয়ার মধ্যে আসে
            diff = abs(last_price - ob['price']) / ob['price']
            if diff <= 0.0015: 
                title = f"🎯 OB Alert: {symbol} ({tf})"
                body = (f"Price hit a {ob['type']}!\n"
                        f"OB Level: {ob['price']}\n"
                        f"Current Price: {last_price}\n"
                        f"Check your chart for entry.")
                send_push(title, body)
                break 

    except Exception as e:
        print(f"Error fetching {symbol} on {tf}: {e}")

if __name__ == "__main__":
    # আপনার চাহিদামত সবগুলো টাইমফ্রেম
    timeframes = ['5m', '10m', '15m', '30m', '1h', '1d']
    symbols = ['BTC/USDT', 'ETH/USDT']
    
    print("Starting market scan for all timeframes...")
    for s in symbols:
        for t in timeframes:
            analyze_market(s, t)
    print("Scan completed.")
