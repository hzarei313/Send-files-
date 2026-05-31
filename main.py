import re
import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import MemorySession
from collections import deque

# --- تنظیمات ربات ---
API_ID = 36850805        
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  
BOT_TOKEN = '8968910927:AAGks2FRyPtu49l90LUAktvroaOgZ-8ELOk'  

SOURCE_GROUP_ID = -1001323267949  
TARGET_CHANNEL_ID = -1002716670503  
# ---------------------------------------------

# استفاده از deque با ظرفیت ۲۰۰ برای جلوگیری از پیام تکراری
processed_messages = deque(maxlen=200)

# راه‌اندازی ربات روی حافظه موقت (مخصوص هاست ابری)
bot = TelegramClient(MemorySession(), API_ID, API_HASH)

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    # بررسی فقط برای ویدیوها
    if event.message.video:
        message_id = event.message.id
        
        # جلوگیری از پیام تکراری
        if message_id in processed_messages:
            return
        processed_messages.append(message_id)
        
        caption = event.message.text or ""
        pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
        
        # پیدا کردن لینک‌ها و انتخاب آخرین مورد
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
        
        # امضای نهایی شما
        signature = "\n\n🆔 @tadvin_eslami"
        final_caption = caption + signature
        
        try:
            # فوروارد مستقیم و بومی روی سرور تلگرام (بدون آپلود)
            await bot.send_message(
                TARGET_CHANNEL_ID, 
                event.message,       # خود پیام اصلی را ارجاع می‌دهد
                caption=final_caption # کپشن جدید را روی آن می‌نشاند
            )
            print(f"[🟢 OK] Video {message_id} forwarded without upload!")
        except Exception as e:
            print(f"[🔴 Error] Cannot forward message. Reason: {e}")

async def main():
    print("[*] Connecting to Telegram...")
    await bot.start(bot_token=BOT_TOKEN)
    print("[+] Telegram client is successfully live and listening!")
    
    # زنده نگه داشتن برنامه به صورت کاملاً آسنکرون
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
