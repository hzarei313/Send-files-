import re
import os
import sys
import asyncio
import logging
from collections import deque
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession

# پیکربندی لایه بافر خروجی جهت ثبت آنی و بدون تاخیر وقایع در کنسول سرور ابری Render
sys.stdout.reconfigure(line_buffering=True)

# تنظیمات پیشرفته سیستم ثبت وقایع استاندارد پایتون برای پایش دقیق رفتار کلاینت
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING
)
logger = logging.getLogger("CloudCoreLogger")

# --- مقادیر ثابت و ساختارهای اتصال احراز هویت ---
API_ID = 36850805        
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  
BOT_TOKEN = '314786408:AAHt1ifaI5wm-yGAUjFzNmOp9P7VgUet0KA'  

# قرار دادن رشته نشست کاملاً پایدار و اصلاح شده (بدون ارور پدینگ)
SESSION_STRING = '1BJWap1wBuyomtkYKifgnqGTpHRMg7JW5FQa_OH-UryEMsHTzhWN8TcYWYYC4ZTQr2wtHfllb-NuA5to_LWndmoF3j9pKAzd-OeNZcp9C6GqQcNsBkkf-SNtAbARVEXaTVKC9GFK-goY6HRc3JqI9r9oXsvubC6EuHxF6Yk9bT-_gB7MV5aUc-kV37rpezvTledDtNuckDbILq7lXTZ2X5g-3MzYHs8zJUnaRn8NZGQWVswyUBVsH2gZXY3xvn1XAK2-KsaEhjiAZblEAZ5qT25VNtV_FIYw2LXilg1gcV5uPjklz7A8PUo6c0R83Un-e3t1j65iJy2fMzJE7NRxDvqtNChCYmMk='

SOURCE_GROUP_ID = -1001323267949  
TARGET_CHANNEL_ID = -1002716670503  
# ---------------------------------------------

# استفاده از بافر حلقوی با طول محدود جهت تضمین عدم نشت حافظه در پردازش پیام‌ها
processed_messages = deque(maxlen=200)

# راه‌اندازی کلاینت بر پایه StringSession پایدار به همراه جعل هویت کاربر معمولی برای فایروال تلگرام
bot = TelegramClient(
    StringSession(SESSION_STRING), 
    API_ID, 
    API_HASH,
    device_model="Desktop Client",
    system_version="Windows 11",
    app_version="4.12.3",
    lang_code="fa"
)

async def handle_web_request(reader, writer):
    """ پاسخ‌دهی به درخواست‌های ارزیابی سلامت بستر ابری (Health Check) """
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
        logger.error(f"خطا در پاسخ‌دهی به ارزیابی سلامت سرور ابری: {e}")
    finally:
        writer.close()

def generate_modified_caption(raw_text: str) -> str:
    """ پردازش متن و ساختاردهی به کپشن نهایی """
    caption = raw_text or ""
    pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
    matches = list(re.finditer(pattern, caption))
    
    if matches:
        last_match = matches[-1]
        caption = caption[:last_match.start()] + "کاری از: " + caption[last_match.start():]
    else:
        caption = caption + "\n\nکاری از: " if caption else "کاری از: "
        
    final_caption = f"{caption}\n\n🆔 @tadvin_eslami"
    return final_caption

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    """ مدیریت و شنود رویدادهای گروه مبدأ """
    if not event.message.video:
        return

    message_id = event.message.id
    if message_id in processed_messages:
        return
    processed_messages.append(message_id)
    
    original_caption = event.message.text or ""
    final_caption = generate_modified_caption(original_caption)
    
    try:
        await bot.send_file(
            TARGET_CHANNEL_ID,
            file=event.message.media,
            caption=final_caption,
            parse_mode='md'
        )
        print(f"[🟢 OK] ویدیو با شناسه {message_id} با موفقیت ارسال گردید.", flush=True)
    except errors.FloodWaitError as e:
        logger.warning(f"محدودیت نرخ ارسال فعال شد. تعلیق به مدت {e.seconds} ثانیه...")
        await asyncio.sleep(e.seconds)
    except errors.RPCError as e:
        logger.error(f"خطای امنیتی تلگرام در پیام {message_id}: {e}")
    except Exception as e:
        logger.error(f"خطای غیرمنتظره در باز ارسال پیام {message_id}: {e}")

async def main():
    port = int(os.environ.get('PORT', 10000))
    print(f"راه‌اندازی سرور وب ناهمگام بومی بر روی پورت {port}...", flush=True)
    server = await asyncio.start_server(handle_web_request, '0.0.0.0', port)

    async with server:
        print("در حال تلاش برای برقراری اتصال ایمن به سرورهای تلگرام...", flush=True)
        try:
            await asyncio.wait_for(bot.start(bot_token=BOT_TOKEN), timeout=20.0)
            print("اتصال و احراز هویت با موفقیت کامل انجام شد!", flush=True)
        except asyncio.TimeoutError:
            print("خطا: فرآیند دست‌دهی با سرورهای تلگرام منقضی گردید!", flush=True)
            return
        except Exception as e:
            print(f"خطای بحرانی در زمان شروع به کار ربات: {e}", flush=True)
            return

        print("[🚀] ربات فعال شده و مانیتورینگ بدون وقفه با موفقیت آغاز گردید.", flush=True)
        await bot.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[🛑] پروسه توسط سیگنال ادمین متوقف گردید.", flush=True)
