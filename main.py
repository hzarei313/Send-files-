import re
import os
from telethon import TelegramClient, events
from telethon.sessions import MemorySession  # تغییر مهم برای هاست‌های ابری
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

@app.route('/')
def home():
    return "Bot is running perfectly on Render!"

def run_flask():
    # رندر به طور پیش‌فرض از پورت 10000 استفاده می‌کند
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# اجرای وب‌سرور در ترد جداگانه
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

# --- بخش تلگرام با سشن موقت حافظه (بدون نیاز به فایل) ---
bot = TelegramClient(MemorySession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

processed_messages = deque(maxlen=200)

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
            # فوروارد بومی تلگرام (بدون آپلود مجدد فایل)
            await bot.send_message(
                TARGET_CHANNEL_ID, 
                event.message,      
                caption=final_caption 
            )
            print(f"ویدیو با موفقیت فوروارد شد. شناسه: {message_id}")
        except Exception as e:
            print(f"خطا در ارسال: {e}")

print("ربات هماهنگ‌شده با رندر روشن شد...")
bot.run_until_disconnected()
