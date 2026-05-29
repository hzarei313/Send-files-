import re
import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import MemorySession
from flask import Flask
from threading import Thread
from collections import deque

# --- تنظیمات ربات ---
API_ID = 36850805        
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  
BOT_TOKEN = '8968910927:AAGks2FRyPtu49l90LUAktvroaOgZ-8ELOk'  

SOURCE_GROUP_ID = -1001323267949  
TARGET_CHANNEL_ID = -1002716670503  
# ---------------------------------------------

app = Flask('')
processed_messages = deque(maxlen=200)

@app.route('/')
def home():
    return "Web server is active. Checking Telegram client..."

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# اجرای وب‌سرور فلاسک به صورت ترد جداگانه
Thread(target=run_flask, daemon=True).start()

# تعریف کلاینت تلگرام با سشن حافظه
bot = TelegramClient(MemorySession(), API_ID, API_HASH)

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    if event.message.video:
        message_id = event.message.id
        
        if message_id in processed_messages:
            return
        
        processed_messages.append(message_id)

        caption = event.message.text or ""
        pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
        matches = list(re.finditer(pattern, caption))
        
        if matches:
            last_match = matches[-1]
            start_idx = last_match.start()
            caption = caption[:start_idx] + "کاری از: " + caption[start_idx:]
        else:
            if caption:
                caption = caption + "\n\nکاری از: "
            else:
                caption = "کاری از: "
        
        signature = "\n\n🆔 @tadvin_eslami"
        final_caption = caption + signature
        
        try:
            await bot.send_message(TARGET_CHANNEL_ID, event.message, caption=final_caption)
            print(f"[-] Video forwarded successfully! ID: {message_id}")
        except Exception as e:
            print(f"[!] Error sending message to channel: {e}")

# تابع اصلی برای مدیریت اجرای امن و باثبات تلپاتون
async def main():
    print("[*] Starting Telegram client...")
    try:
        # متصل شدن و لاگین آسنکرون با توکن ربات
        await bot.start(bot_token=BOT_TOKEN)
        print("[+] Telegram client connected and authorized successfully!")
        
        # منتظر ماندن برای دریافت پیام‌ها
        await bot.run_until_disconnected()
    except Exception as e:
        print(f"[CRITICAL] Telegram client crashed: {e}")

if __name__ == '__main__':
    # اجرای چرخه آسنکرون پایتون
    asyncio.run(main())
