import os
import ccxt
import pandas as pd
import requests

# আপনার Pushbullet টোকেন যা গিটহাব সিক্রেটস এ সেভ করা আছে
PUSHBULLET_TOKEN = os.getenv('PUSHBULLET_TOKEN')

def send_push(title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {'Access-Token': PUSHBULLET_TOKEN, 'Content-Type': 'application/json'}
    data = {'type': 'note', 'title': title, 'body': body}
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Push Error: {e}")

def detect_smc_ob(df):
    # গত ৫০টি ক্যান্ডেলের মধ্যে শক্তিশালী এবং ফ্রেশ অর্ডার ব্লক খোঁজা
    for i in range(len(df)-50, len(df)-2):
        # Bullish OB লজিক: রেড ক্যান্ডেলের পর শক্তিশালী বুলিশ মুভমেন্ট
        if df['close'].iloc[i] < df['open'].iloc[i]: 
            if df['close'].iloc[i+1] > df['high'].iloc[i] or df['close'].iloc[i+2] > df['high'].iloc[i]:
                ob_low = df['low'].iloc[i]
                ob_high = df['high'].iloc[i]
                
                # চেক করা হচ্ছে এই জোনটি কি আগে কোনো ক্যান্ডেল দিয়ে টাচ হয়েছে? (Freshness Check)
                future_lows = df['low'].iloc[i+1:]
                if future_lows.min() > ob_low:
                    return ob_low, ob_high
    return None, None

def analyze_market(symbol, tf):
    try:
        exchange = ccxt.mexc()
        # নির্দিষ্ট টাইমফ্রেমের ডাটা ফেচ করা
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        last_price = df['close'].iloc[-1]
        ob_low, ob_high = detect_smc_ob(df)
        
        if ob_low and ob_high:
            # ১. নতুন ওবি তৈরি হওয়ার নোটিফিকেশন (প্রাইস যখন ওবি-র উপরে থাকে)
            if last_price > ob_high:
                send_push(f"✨ NEW OB CREATED: {symbol} ({tf})", 
                          f"টাইমফ্রেম: {tf}\nনতুন বুলিশ ওবি জোন তৈরি হয়েছে।\nজোন: {round(ob_low, 2)} - {round(ob_high, 2)}")
            
            # ২. ওবি-তে এন্ট্রি বা টাচ করার নোটিফিকেশন (প্রাইস যখন জোনের ভেতর থাকে)
            elif last_price <= (ob_high * 1.0005) and last_price >= (ob_low * 0.9995):
                # এন্ট্রি সিগন্যালে TP এবং SL যোগ করা হয়েছে
                stop_loss = ob_low - (ob_low * 0.001)
                risk = ob_high - stop_loss
                take_profit = ob_high + (risk * 2)

                message = (f"প্রাইস এখন বুলিশ ওবি জোনের ভেতরে!\n\n"
                           f"🛒 বর্তমান প্রাইস: {last_price}\n"
                           f"🎯 টেক প্রফিট (TP): {round(take_profit, 2)}\n"
                           f"🛑 স্টপ লস (SL): {round(stop_loss, 2)}")
                send_push(f"🎯 OB ENTRY: {symbol} ({tf})", message)

    except Exception as e:
        print(f"Error checking {tf}: {e}")

if __name__ == "__main__":
    # আপনার চাহিদা অনুযায়ী সবকটি টাইমফ্রেম এখানে দেওয়া হয়েছে
    timeframes = ['5m', '10m', '15m', '30m', '1h', '1d']
    symbols = ['BTC/USDT'] # আপনি চাইলে এখানে আরও কয়েন যোগ করতে পারেন
    
    for s in symbols:
        for tf in timeframes:
            analyze_market(s, tf)
