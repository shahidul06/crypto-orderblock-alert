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

def find_strict_ob(df, tf):
    # গত ৫০টি ক্যান্ডেল চেক করবে যাতে বড় টাইমফ্রেমের ওবি-ও ধরা পড়ে
    for i in range(len(df)-50, len(df)-3):
        # Bullish OB লজিক: রেড ক্যান্ডেলের পর শক্তিশালী বুলিশ ইমপালস
        if df['close'].iloc[i] < df['open'].iloc[i]:
            red_body = abs(df['close'].iloc[i] - df['open'].iloc[i])
            # পরবর্তী ৩টি ক্যান্ডেলের মোট মুভমেন্ট যদি রেড ক্যান্ডেলের ৩ গুণ হয়
            move_after = df['close'].iloc[i+3] - df['open'].iloc[i+1]
            
            if move_after > (red_body * 3):
                ob_high = df['high'].iloc[i]
                ob_low = df['low'].iloc[i]
                
                # Freshness Check: জোনটি কি আগে টাচ হয়েছে?
                future_lows = df['low'].iloc[i+1:]
                if future_lows.min() > ob_high:
                    return ob_low, ob_high
    return None, None

def analyze_market(symbol, tf):
    try:
        exchange = ccxt.mexc()
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        last_price = df['close'].iloc[-1]
        ob_low, ob_high = find_strict_ob(df, tf)
        
        if ob_low and ob_high:
            # প্রাইস যখন জোনের একদম কাছে বা ভেতরে থাকবে (০.০৩% প্রিসিশন)
            if last_price <= (ob_high * 1.0003) and last_price >= (ob_low * 0.9997):
                send_push(f"🎯 OB TOUCH: {symbol} ({tf})", 
                          f"Price is EXACTLY inside your Bullish OB!\n"
                          f"OB Zone: {round(ob_low, 2)} - {round(ob_high, 2)}\n"
                          f"Current Price: {last_price}\n"
                          f"Check Chart Now!")

    except Exception as e:
        print(f"Error on {tf}: {e}")

if __name__ == "__main__":
    # আপনার রিকোয়েস্ট অনুযায়ী সবগুলো টাইমফ্রেম
    timeframes = ['5m', '10m', '15m', '30m', '1h', '1d']
    for tf in timeframes:
        analyze_market('BTC/USDT', tf)
