import os
import ccxt
import requests
import pandas as pd

# কনফিগারেশন
PUSHBULLET_TOKEN = os.getenv('PUSHBULLET_TOKEN')
SYMBOLS = ['BTC/USDT', 'ETH/USDT']
TIMEFRAMES = ['5m', '15m', '1h']

exchange = ccxt.mexc()

def send_push_notification(title, body):
    if not PUSHBULLET_TOKEN:
        print("Pushbullet Token not found!")
        return
    
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'}
    data = {'type': 'note', 'title': title, 'body': body}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Notification sent!")
    else:
        print(f"Error: {response.text}")

def analyze_market(symbol, tf):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=50)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        last_price = df['close'].iloc[-1]
        
        signals = []

        # ১. হাই ভলিউম চেক
        avg_volume = df['volume'].tail(20).mean()
        if df['volume'].iloc[-1] > (avg_volume * 1.5):
            signals.append("- High Volume OB")

        # ২. FVG চেক
        if df['low'].iloc[-1] > df['high'].iloc[-3]:
            signals.append("- Bullish FVG")
        elif df['high'].iloc[-1] < df['low'].iloc[-3]:
            signals.append("- Bearish FVG")

        # ৩. CHoCH চেক
        recent_high = df['high'].iloc[-15:-1].max()
        if df['close'].iloc[-1] > recent_high:
            signals.append("- CHoCH Bullish")

        if signals:
            title = f"Signal: {symbol} ({tf})"
            body = f"Price: {last_price}\n" + "\n".join(signals)
            send_push_notification(title, body)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # কানেকশন টেস্ট করার জন্য একটি মেসেজ
    send_push_notification("System Active", "বট এখন Pushbullet এর সাথে কানেক্টেড!")
    
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            analyze_market(symbol, tf)
