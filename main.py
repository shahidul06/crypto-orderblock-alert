import os
import requests
import pandas as pd
import ccxt

# কনফিগারেশন
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def run_demo():
    print("ডেমো নোটিফিকেশন পাঠানো হচ্ছে...")
    
    # এটি একটি ডেমো মেসেজ যা সরাসরি যাবে
    demo_msg = (
        "🔔 *SMC Alert: Demo Notification*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✅ *Connection:* Successful\n"
        "📊 *Status:* Script is Running\n"
        "🚀 *Strategy:* Order Block & FVG\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "আপনার বট এখন মার্কেট সিগন্যাল পাঠানোর জন্য প্রস্তুত!"
    )
    
    send_telegram_message(demo_msg)

if __name__ == "__main__":
    # টোকেন ও আইডি আছে কিনা চেক করা
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_TOKEN বা TELEGRAM_CHAT_ID পাওয়া যায়নি! GitHub Secrets চেক করুন।")
    else:
        run_demo()
