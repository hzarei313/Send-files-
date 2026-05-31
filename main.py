import re
import os
from telethon import TelegramClient, events
from telethon.sessions import MemorySession # برای جلوگیری از قفل شدن فایل سشن روی هاست
from flask import Flask
from threading import Thread
from collections import deque

# --- تنظیمات ربات (این مقادیر را تغییر دهید) ---
API_ID = 36850805        
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  
BOT_TOKEN = '8968910927:AAGks2FRyPtu49l90LUAktvroaOgZ-8ELOk'  

SOURCE_GROUP_ID = -1001323267949  
TARGET_CHANNEL_ID = -1002716670503  
# ---------------------------------------------

app = Flask('')
# استفاده از deque برای ذخیره آیدی پیام‌های پردازش شده (جلوگیری از ارسال تکراری)
processed_messages = deque(maxlen=200)

@app.route('/')
def home():
    return "Bot is running efficiently!"

def run():
    # رندر پورت را در این متغیر قرار می‌دهد (معمولاً 10000)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# اجرای وب‌سرور فلاسک در ترد پس‌زمینه
Thread(target=run, daemon=True).start()

print("وب‌سرور فعال شد. در حال متصل شدن به تلگرام...")

# استفاده از MemorySession باعث می‌شود ربات روی حافظه موقت اجرا شود و فایل هارد را درگیر نکند
bot = TelegramClient(MemorySession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    # ۱. فقط ویدیوها پردازش شوند
    if event.message.video:
        message_id = event.message.id
        
        # ۲. جلوگیری از پردازش پیام تکراری
        if message_id in processed_messages:
            return
        processed_messages.append(message_id)
        
        caption = event.message.text or ""
        pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
        
        # پیدا کردن تمام لینک‌ها و انتخاب آخرین لینک (برای عبارت کاری از)
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
        
        # اضافه کردن امضا
        signature = "\n\n🆔 @tadvin_eslami"
        final_caption = caption + signature
        
        try:
            # ۳. شاه‌کلید اصلی: ارسال خودِ پیام (فوروارد بومی با کپشن جدید بدون آپلود)
            await bot.send_message(
                TARGET_CHANNEL_ID, 
                event.message,       # به جای فایل، خود پیام را می‌فرستیم
                caption=final_caption # کپشن جدید را روی آن ست می‌کنیم
            )
            print(f"[Success] Video {message_id} forwarded without upload!")
        except Exception as e:
            print(f"[Error] Failed to forward: {e}")

print("ربات ضد تکرار و بدون آپلود فعال شد و در حال گوش دادن است...")
bot.run_until_disconnected()
