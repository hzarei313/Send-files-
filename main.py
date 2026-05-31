import re
import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import MemorySession
from flask import Flask
from collections import deque

# --- تنظیمات ربات (مشخصات شما) ---
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
    return "Bot and Web Server are running perfectly together!"

# راه‌اندازی کلاینت تلگرام با سشن حافظه
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
            # فوروارد بومی تلگرام بدون دانلود و آپلود
            await bot.send_message(TARGET_CHANNEL_ID, event.message, caption=final_caption)
            print(f"[🟢 Success] Video {message_id} forwarded seamlessly.")
        except Exception as e:
            print(f"[🔴 Error] Forwarding failed: {e}")

# تابع اصلی برای مدیریت همزمان فلاسک و تلگرام بدون تداخل تردها
async def main():
    print("[*] Starting Telegram client...")
    await bot.start(bot_token=BOT_TOKEN)
    print("[+] Telegram client connected successfully!")

    # تنظیم پورت رندر
    port = int(os.environ.get('PORT', 10000))
    
    # راه اندازی فلاسک به صورت آسنکرون بدون نیاز به Threading سنتی
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    
    config = Config()
    config.bind = [f"0.0.0.0:{port}"]
    
    print(f"[*] Starting Web Server on port {port}...")
    
    # اجرای همزمان سرور وب و ربات تلگرام در یک لوپ واحد
    await asyncio.gather(
        serve(app, config),
        bot.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())
