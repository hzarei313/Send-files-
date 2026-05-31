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
bot = TelegramClient(MemorySession(), API_ID, API_HASH)

# --- وب‌سرور آسنکرون فوق‌العاده سبک بومی (جایگزین فلاسک و هایپرکورن) ---
async def handle_web_request(reader, writer):
    """پاسخگویی استاندارد به پینگ‌های رندر جهت جلوگیری از کرش سرور"""
    data = await reader.read(1024)
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Length: 22\r\n"
        "Connection: close\r\n\r\n"
        "Bot is running great!"
    )
    writer.write(response.encode('utf-8'))
    await writer.drain()
    writer.close()
    await writer.wait_closed()

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
            # فوروارد بومی تلگرام بدون دانلود و آپلود مجدد
            await bot.send_message(TARGET_CHANNEL_ID, event.message, caption=final_caption)
            print(f"[🟢 OK] Video {message_id} forwarded successfully.")
        except Exception as e:
            print(f"[🔴 Error] Forwarding failed: {e}")

async def main():
    print("[*] Starting Telegram client...")
    await bot.start(bot_token=BOT_TOKEN)
    print("[+] Telegram client connected!")

    # تنظیم پورت رندر
    port = int(os.environ.get('PORT', 10000))
    
    print(f"[*] Starting Native Web Server on port {port}...")
    # راه‌اندازی سرور وب بومی پایتون بدون نیاز به هیچ کتابخانه جانبی اضافه
    web_server = await asyncio.start_server(handle_web_request, '0.0.0.0', port)

    # اجرای همزمان سرور وب و ربات تلگرام در یک چرخه پایدار
    async with web_server:
        await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
