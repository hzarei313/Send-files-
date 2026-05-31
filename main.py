import re
import os
import asyncio
import sys
from telethon import TelegramClient, events
from telethon.sessions import MemorySession
from collections import deque

# پیکربندی لایه بافر خروجی جهت ثبت آنی وقایع در کنسول سرور ابری Render
sys.stdout.reconfigure(line_buffering=True)

# --- مقادیر ثابت و ساختارهای اتصال احراز هویت ---
API_ID = 36850805        
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  
BOT_TOKEN = '8968910927:AAGks2FRyPtu49l90LUAktvroaOgZ-8ELOk'  

SOURCE_GROUP_ID = -1001323267949  
TARGET_CHANNEL_ID = -1002716670503  
# ---------------------------------------------

# بکارگیری بافر حلقوی با طول محدود جهت تضمین عدم نشت حافظه و پایش پیام‌های تکراری
processed_messages = deque(maxlen=200)

# راه‌اندازی کلاینت بر پایه حافظه موقت (Memory Session) متناسب با ساختار توزیع‌شده سرورهای ابری
bot = TelegramClient(MemorySession(), API_ID, API_HASH)

async def handle_web_request(reader, writer):
    """
    پاسخ‌دهی به درخواست‌های ارزیابی سلامت بستر ابری (Health Check) بر اساس پروتکل HTTP/1.1.
    استفاده از کاراکترهای اسکی پایان خط منطبق بر استاندارد RFC 7230.
    """
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
    except Exception as e:
        print(f" Failed to respond to health check: {e}", flush=True)
    finally:
        writer.close()

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    """
    مدیریت و شنود رویدادهای مربوط به پیام‌های جدید گروه مبدأ.
    فیلتر و پایش ساختارهای مالتی‌مدیا و بازنویسی کپشن رسانه‌ها.
    """
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
            caption = caption[:last_match.start()] + "کاری از: " + caption[last_match.start():]
        else:
            caption = caption + "\n\nکاری از: " if caption else "کاری از: "
            
        final_caption = caption + "\n\n🆔 @tadvin_eslami"
        
        try:
            # مهندسی مجدد کپشن بدون نقض امضای متد ارسال تلگرام
            # جهش مستقیم بر روی خصیصه‌های شیء پیام جهت حفظ متادیتای اصلی ویدیو روی سرور تلگرام
            event.message.message = final_caption
            event.message.entities = None  # بازنشانی نهادهای متنی جهت دفع خطاهای احتمالی آفست کاراکتر
            
            await bot.send_message(
                TARGET_CHANNEL_ID, 
                event.message
            )
            print(f"[🟢 OK] Video {message_id} forwarded successfully with modified caption.", flush=True)
        except Exception as e:
            print(f"[🔴 Error] Cannot forward message {message_id}: {e}", flush=True)

async def main():
    port = int(os.environ.get('PORT', 10000))
    print(f" Starting non-blocking Native Web Server on port {port}...", flush=True)
    server = await asyncio.start_server(handle_web_request, '0.0.0.0', port)

    async with server:
        print(" Initiating secure connection to Telegram servers...", flush=True)
        try:
            await asyncio.wait_for(bot.start(bot_token=BOT_TOKEN), timeout=15.0)
            print(" Connection established and authenticated successfully!", flush=True)
        except asyncio.TimeoutError:
            print(" Connection handshake with Telegram timed out!", flush=True)
            return
        except Exception as e:
            print(f" Client startup aborted due to initialization failure: {e}", flush=True)
            return

        print("[🚀] Deployment initialization finished. Bot is actively monitoring...", flush=True)
        
        # بکارگیری بهینه‌ترین متد بومی برای فعال نگه داشتن موتور رویدادها بدون بارگذاری کاذب پردازنده
        await bot.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[🛑] Process terminated by administrator signal.", flush=True)
