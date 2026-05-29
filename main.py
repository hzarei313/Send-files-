import re
import os
from telethon import TelegramClient, events
from telethon.sessions import MemorySession
from flask import Flask
from threading import Thread
from collections import deque

# --- تنظیمات ربات (اطلاعات شما) ---
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
    return "Web server is active!"

def run_flask():
    # تنظیم پورت هماهنگ با رندر
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# اجرای وب سرور فلاسک در پس‌زمینه
Thread(target=run_flask, daemon=True).start()

print("وب‌سرور روشن شد. در حال اتصال به تلگرام...")

# راه‌اندازی ربات با سشن حافظه موقت مخصوص هاست ابری
bot = TelegramClient(MemorySession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    # فقط و فقط پیام‌های حاوی ویدیو پردازش شوند
    if event.message.video:
        message_id = event.message.id
        
        # جلوگیری از ارسال ویدیوهای تکراری
        if message_id in processed_messages:
            return
        
        processed_messages.append(message_id)

        # پردازش متن کپشن
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
            # فوروارد بومی تلگرام بدون دانلود، آپلود و پردازش مجدد روی سرور
            await bot.send_message(
                TARGET_CHANNEL_ID, 
                event.message,      
                caption=final_caption 
            )
            print(f" ویدیو با موفقیت فوروارد شد. شناسه: {message_id}")
        except Exception as e:
            print(f"خطا در ارسال پیام به کانال: {e}")

print("ربات تلگرام با موفقیت فعال شد و در حال گوش دادن به پیام‌هاست...")
bot.run_until_disconnected()
