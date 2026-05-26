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

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    if event.message.video:
        caption = event.message.text or ""
        
        # الگوی تشخیص آیدی یا لینک
        pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
        match = re.search(pattern, caption)
        
        if match:
            # اگر آیدی یا لینک بود، "کاری از:" را دقیقاً قبل از آن می‌گذارد
            start_idx = match.start()
            caption = caption[:start_idx] + "کاری از: " + caption[start_idx:]
        else:
            # اگر هیچ آیدی یا لینکی نبود
            if caption:
                caption = "کاری از: " + caption
            else:
                caption = "کاری از: " # اگر ویدیو اصلاً کپشن نداشت
        
        # اضافه کردن امضا در دو خط پایین‌تر برای همه پیام‌ها
        signature = "\n\n🆔 @tadvin_eslami"
        final_caption = caption + signature
        
        await bot.send_file(TARGET_CHANNEL_ID, event.message.video, caption=final_caption)

print("ربات با موفقیت آپدیت شد!")
bot.run_until_disconnected()
