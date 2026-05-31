import re
import os
import asyncio
import sys
from telethon import TelegramClient, events
from telethon.sessions import MemorySession
from collections import deque

# فعال کردن ارسال آنی لاگ‌ها به سرور رندر
sys.stdout.reconfigure(line_buffering=True)

# --- تنظیمات ربات ---
API_ID = 36850805        
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  
BOT_TOKEN = '8968910927:AAGks2FRyPtu49l90LUAktvroaOgZ-8ELOk'  

SOURCE_GROUP_ID = -1001323267949  
TARGET_CHANNEL_ID = -1002716670503  
# ---------------------------------------------

processed_messages = deque(maxlen=200)
bot = TelegramClient(MemorySession(), API_ID, API_HASH)

async def handle_web_request(reader, writer):
    try:
        await reader.read(1024)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\nConnection: close\r\n\r\nBot is Active!"
        writer.write(response.encode('utf-8'))
        await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()

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
            caption = caption[:last_match.start()] + "کاری از: " + caption[last_match.start():]
        else:
            caption = caption + "\n\nکاری از: " if caption else "کاری از: "
            
        final_caption = caption + "\n\n🆔 @tadvin_eslami"
        
        try:
            # --- اصلاح اصلی: تغییر caption به text برای فوروارد بومی ---
            await bot.send_message(
                TARGET_CHANNEL_ID, 
                event.message, 
                text=final_caption  # تلپاتون برای پیام‌های کامل متن جدید را در text می‌گیرد
            )
            print(f"[🟢 OK] Video {message_id} forwarded successfully.", flush=True)
        except Exception as e:
            print(f"[🔴 Error] Cannot forward: {e}", flush=True)

async def main():
    port = int(os.environ.get('PORT', 10000))
    print(f"[1] Starting Native Web Server on port {port}...", flush=True)
    server = await asyncio.start_server(handle_web_request, '0.0.0.0', port)

    async with server:
        print("[2] Connecting to Telegram API...", flush=True)
        try:
            await asyncio.wait_for(bot.start(bot_token=BOT_TOKEN), timeout=15.0)
            print("[3] Telegram client connected successfully!", flush=True)
        except asyncio.TimeoutError:
            print("[❌ CRITICAL] Connection to Telegram Timed Out!", flush=True)
            return
        except Exception as e:
            print(f"[❌ ERROR] Telegram login failed: {e}", flush=True)
            return

        print("[🚀] System is fully live and listening for videos...", flush=True)
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
