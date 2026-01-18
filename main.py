import os
import ccxt
import requests
import pandas as pd

# কনফিগারেশন
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SYMBOLS = ['BTC/USDT', 'ETH/USDT']
TIMEFRAMES = ['5m', '15m', '1h', '1d']

exchange = ccxt.mexc()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, json=payload)

def analyze_market(symbol, tf):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=50)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        last_price = df['close'].iloc[-1]
        signals = []

        # ১. হাই ভলিউম অর্ডার ব্লক
        avg_volume = df['volume'].tail(20).mean()
        if df['volume'].iloc[-1] > (avg_volume * 1.8):
            signals.append(f"⚠️ *High Volume OB detected!*")

        # ২. ফেয়ার ভ্যালু গ্যাপ (FVG)
        if df['low'].iloc[-1] > df['high'].iloc[-3]:
            signals.append(f"🟢 *Bullish FVG found!*")
        elif df['high'].iloc[-1] < df['low'].iloc[-3]:
            signals.append(f"🔴 *Bearish FVG found!*")

        # ৩. চেঞ্জ অফ ক্যারেক্টার (CHoCH)
        recent_high = df['high'].iloc[-15:-1].max()
        recent_low = df['low'].iloc[-15:-1].min()
        if df['close'].iloc[-1] > recent_high:
            signals.append(f"🔄 *CHoCH: Bullish Breakout!*")
        elif df['close'].iloc[-1] < recent_low:
            signals.append(f"🔄 *CHoCH: Bearish Breakout!*")

        if signals:
            msg = f"🚀 *New Signal: {symbol} ({tf})*\nPrice: `{last_price}`\n" + "\n".join(signals)
            send_telegram_message(msg)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            analyze_market(symbol, tf)
