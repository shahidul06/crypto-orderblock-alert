import os
import ccxt
import requests
import pandas as pd

# Pushbullet টোকেন (গিটহাব সিক্রেটস থেকে আসবে)
PUSHBULLET_TOKEN = os.getenv('PUSHBULLET_TOKEN')

# যে কয়েনগুলো এবং টাইমফ্রেমগুলো আপনি চেয়েছিলেন
SYMBOLS = ['BTC/USDT', 'ETH/USDT']
TIMEFRAMES = ['5m', '10m', '15m', '30m', '1h', '1d']

def send_push(title, body):
    if not PUSHBULLET_TOKEN:
        print("Error: Pushbullet Token not found!")
        return
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'}
    data = {'type': 'note', 'title': title, 'body': body}
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Push Error: {e}")

def analyze_market(symbol, tf):
    try:
        # MEXC থেকে ডাটা কানেকশন চেক
        exchange = ccxt.mexc()
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=50)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        last_price = df['close'].iloc[-1]
        print(f"Checking {symbol} on {tf}... Current Price: {last_price}") # গিটহাব লগে দেখা যাবে

        signals = []

        # ১. হাই ভলিউম (অর্ডার ব্লক হওয়ার সম্ভাবনা)
        avg_volume = df['volume'].tail(20).mean()
        if df['volume'].iloc[-1] > (avg_volume * 1.8):
            signals.append("⚠️ High Volume (Possible OB)")

        # ২. ফেয়ার ভ্যালু গ্যাপ (FVG)
        if df['low'].iloc[-1] > df['high'].iloc[-3]:
            signals.append("🟢 Bullish FVG Found")
        elif df['high'].iloc[-1] < df['low'].iloc[-3]:
            signals.append("🔴 Bearish FVG Found")

        # ৩. ট্রেন্ড চেঞ্জ (CHoCH)
        recent_high = df['high'].iloc[-15:-1].max()
        recent_low = df['low'].iloc[-15:-1].min()
        if df['close'].iloc[-1] > recent_high:
            signals.append("🔄 CHoCH: Bullish Breakout")
        elif df['close'].iloc[-1] < recent_low:
            signals.append("🔄 CHoCH: Bearish Breakout")

        # যদি কোনো সিগন্যাল পাওয়া যায় তবেই পুশ পাঠাবে
        if signals:
            title = f"🚀 {symbol} Signal ({tf})"
            body = f"Price: {last_price}\n" + "\n".join(signals)
            send_push(title, body)

    except Exception as e:
        print(f"Error fetching {symbol} {tf}: {e}")

if __name__ == "__main__":
    print("Market Scan Started for all Timeframes...")
    
    # সবগুলো কয়েন এবং টাইমফ্রেম লুপ আকারে চেক করবে
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            analyze_market(symbol, tf)
            
    print("Market Scan Completed.")
