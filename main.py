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

def detect_smc_ob(df):
    for i in range(len(df)-50, len(df)-5):
        if df['close'].iloc[i] < df['open'].iloc[i]: # Red Candle
            if df['close'].iloc[i+1] > df['high'].iloc[i] or df['close'].iloc[i+2] > df['high'].iloc[i]:
                ob_low = df['low'].iloc[i]
                ob_high = df['high'].iloc[i]
                
                future_lows = df['low'].iloc[i+1:]
                if future_lows.min() > ob_low:
                    return ob_low, ob_high
    return None, None

def analyze_market(symbol, tf):
    try:
        exchange = ccxt.mexc()
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        last_price = df['close'].iloc[-1]
        ob_low, ob_high = detect_smc_ob(df)
        
        if ob_low and ob_high:
            # TP এবং SL ক্যালকুলেশন (SMC লজিক অনুযায়ী)
            # স্টপ লস হবে অর্ডার ব্লকের ঠিক নিচে
            stop_loss = ob_low - (ob_low * 0.001) 
            # টেক প্রফিট হবে রিস্কের দ্বিগুণ (RR 1:2)
            risk = ob_high - stop_loss
            take_profit = ob_high + (risk * 2)

            # প্রাইস যখন জোনের ভেতরে থাকবে
            if last_price <= (ob_high * 1.0005) and last_price >= (ob_low * 0.9995):
                message = (f"Price is INSIDE Bullish OB!\n\n"
                           f"🛒 Entry: {last_price}\n"
                           f"🎯 TP: {round(take_profit, 2)}\n"
                           f"🛑 SL: {round(stop_loss, 2)}\n"
                           f"⚖️ Risk-Reward: 1:2")
                send_push(f"✅ ENTRY ALERT: {symbol} ({tf})", message)

    except Exception as e:
        print(f"Error on {tf}: {e}")

if __name__ == "__main__":
    timeframes = ['5m', '10m', '15m', '30m', '1h', '1d']
    for tf in timeframes:
        analyze_market('BTC/USDT', tf)
