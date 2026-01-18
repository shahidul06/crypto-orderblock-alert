import os
import ccxt
import requests
import pandas as pd

# Pushbullet টোকেন সংগ্রহ
PUSHBULLET_TOKEN = os.getenv('PUSHBULLET_TOKEN')

def send_push(title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'}
    data = {'type': 'note', 'title': title, 'body': body}
    requests.post(url, headers=headers, json=data)

def analyze_market(symbol, tf):
    try:
        exchange = ccxt.mexc()
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=50)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        last_price = df['close'].iloc[-1]
        
        signals = []
        # কন্ডিশন ১: হাই ভলিউম
        if df['volume'].iloc[-1] > (df['volume'].tail(20).mean() * 1.5):
            signals.append("⚠️ High Volume detected")
        # কন্ডিশন ২: FVG
        if df['low'].iloc[-1] > df['high'].iloc[-3]:
            signals.append("🟢 Bullish FVG")
        elif df['high'].iloc[-1] < df['low'].iloc[-3]:
            signals.append("🔴 Bearish FVG")

        if signals:
            send_push(f"Signal: {symbol} ({tf})", f"Price: {last_price}\n" + "\n".join(signals))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    symbols = ['BTC/USDT', 'ETH/USDT']
    timeframes = ['15m', '1h']
    for s in symbols:
        for t in timeframes:
            analyze_market(s, t)
