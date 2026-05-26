import re
import os
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# --- تنظیمات ربات (این مقادیر را تغییر دهید) ---
API_ID = 36850805        # شماره ای‌پی‌آی شما
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  # ای‌پ‌آی هش شما
BOT_TOKEN = '8968910927:AAGks2FRyPtu49l90LUAktvroaOgZ-8ELOk'  # توکن ربات شما

SOURCE_GROUP_ID = -1001323267949  # آیدی عددی گروه مبدا
TARGET_CHANNEL_ID = -1002716670503  # آیدی عددی کانال مقصد
# ---------------------------------------------

app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

Thread(target=run).start()

bot = TelegramClient('caption_bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# یک لیست موقت برای ذخیره آیدی پیام‌های پردازش شده
processed_messages = set()

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    if event.message.video:
        # جلوگیری از ارسال پیام تکراری
        if event.message.id in processed_messages:
            return
        
        # اضافه کردن آیدی پیام به لیست تکراری‌ها
        processed_messages.add(event.message.id)
        
        # اگر لیست خیلی بزرگ شد، برای صرفه‌جویی در حافظه آن را خالی کن
        if len(processed_messages) > 100:
            processed_messages.clear()

        caption = event.message.text or ""
        
        # الگوی تشخیص آیدی یا لینک
        pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
        match = re.search(pattern, caption)
        
        if match:
            start_idx = match.start()
            caption = caption[:start_idx] + "کاری از: " + caption[start_idx:]
        else:
            if caption:
                caption = "کاری از: " + caption
            else:
                caption = "کاری از: "
        
        # اضافه کردن امضا
        signature = "\n\n🆔 @tadvin_eslami"
        final_caption = caption + signature
        
        try:
            await bot.send_file(TARGET_CHANNEL_ID, event.message.video, caption=final_caption)
        except Exception as e:
            print(f"Error: {e}")

print("ربات ضد تکرار روشن شد!")
bot.run_until_disconnected()
