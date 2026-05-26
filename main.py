import re
import os
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# --- تنظیمات ربات (این مقادیر را تغییر دهید) ---
API_ID = 1234567        # شماره ای‌پی‌آی شما
API_HASH = 'your_api_hash'  # ای‌پ‌آی هش شما
BOT_TOKEN = 'your_bot_token'  # توکن ربات شما

SOURCE_GROUP_ID = -1001234567890  # آیدی عددی گروه مبدا
TARGET_CHANNEL_ID = -1000987654321  # آیدی عددی کانال مقصد
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
        pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
        match = re.search(pattern, caption)
        
        if match:
            start_idx = match.start()
            caption = caption[:start_idx] + "کاری از: " + caption[start_idx:]
        
        signature = "\n\n🆔 @tadvin_eslami"
        final_caption = caption + signature
        
        await bot.send_file(TARGET_CHANNEL_ID, event.message.video, caption=final_caption)

print("ربات آنلاین شد!")
bot.run_until_disconnected()
