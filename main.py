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

processed_messages = deque(maxlen=200)

# سشن حافظه برای پایداری در هاست ابری
bot = TelegramClient(MemorySession(), API_ID, API_HASH)

# --- وب‌سرور آسنکرون فوق‌العاده سبک برای رندر ---
async def handle_web_request(reader, writer):
    """پاسخ آنی به پینگ‌های رندر برای زنده ماندن هاست"""
    try:
        await reader.read(1024)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            "Content-Length: 14\r\n"
            "Connection: close\r\n\r\n"
            "Bot is Active!"
        )
        writer.write(response.encode('utf-8'))
        await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()

# --- لیسنر پیام‌های تلگرام ---
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
            # فوروارد بومی (بدون ۱ کیلوبایت دانلود یا آپلود)
            await bot.send_message(TARGET_CHANNEL_ID, event.message, caption=final_caption)
            print(f"[🟢 OK] Video {message_id} forwarded successfully.")
        except Exception as e:
            print(f"[🔴 Error] Cannot forward: {e}")

# --- تابع اصلی و هماهنگ‌کننده چرخه‌ها ---
async def main():
    # ۱. اتصال به تلگرام
    print("[*] Connecting to Telegram...")
    await bot.start(bot_token=BOT_TOKEN)
    print("[+] Telegram client connected!")

    # ۲. راه‌اندازی وب‌سرور روی پورت رندر
    port = int(os.environ.get('PORT', 10000))
    print(f"[*] Starting Web Server on port {port}...")
    server = await asyncio.start_server(handle_web_request, '0.0.0.0', port)

    # ۳. اجرای موازی و بدون مسدودیِ وب‌سرور و تلگرام
    async with server:
        print("[🚀] Everything is live and running perfectly!")
        # این متد به جای run_until_disconnected استفاده میشه تا لوپ باز بمونه
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    # اجرای کل کلاینت در یک چرخه آسنکرون واحد
    asyncio.run(main())
