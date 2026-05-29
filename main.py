import re
import os
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread
from collections import deque

# --- تنظیمات ربات (این مقادیر را تغییر دهید) ---
API_ID = 36850805        # شماره ای‌پی‌آی شما
API_HASH = 'f3e90cffb1a5ca214883a0b886ad62b4'  # ای‌پ‌آی هش شما
BOT_TOKEN = '8968910927:AAGks2FRyPtu49l90LUAktvroaOgZ-8ELOk'  # توکن ربات شما

SOURCE_GROUP_ID = -1001323267949  # آیدی عددی گروه مبدا
TARGET_CHANNEL_ID = -1002716670503  # آیدی عددی کانال مقصد
# ---------------------------------------------

# وب‌سرور برای زنده نگه داشتن ربات در هاست
app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly!"

# اجرای وب‌سرور Flask در یک تابع مجزا برای زنده نگه داشتن ربات
def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ساخت و شروع ترد فلاسک به صورت Daemon جهت جلوگیری از تداخل با تلگرام
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

# --- بخش تلگرام (Telethon) ---

# راه‌اندازی کلاینت تلگرام
bot = TelegramClient('caption_bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# استفاده از deque با ظرفیت ثابت ۲۰۰ برای مدیریت هوشمند پیام‌های تکراری
processed_messages = deque(maxlen=200)

@bot.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    # این شرط تضمین می‌کند که ربات *فقط و فقط* پیام‌های حاوی ویدیو را پردازش کند
    if event.message.video:
        message_id = event.message.id
        
        # جلوگیری از پردازش پیام‌های تکراری
        if message_id in processed_messages:
            return
        
        processed_messages.append(message_id)

        # دریافت متن کپشن اصلی ویدیو
        caption = event.message.text or ""
        
        # الگوی تشخیص آیدی یا لینک
        pattern = r'(@\w+|https?://[^\s]+|t\.me/[^\s]+)'
        
        # پیدا کردن تمام آیدی‌ها و لینک‌های درون متن به صورت لیست
        matches = list(re.finditer(pattern, caption))
        
        if matches:
            # انتخاب دقیقاً آخرین آیدی یا لینک پیدا شده (تولیدکننده)
            last_match = matches[-1]
            start_idx = last_match.start()
            
            # تزریق عبارت درست قبل از آخرین آیدی/لینک
            caption = caption[:start_idx] + "کاری از: " + caption[start_idx:]
        else:
            # اگر هیچ آیدی یا لینکی نبود، عبارت به انتهای متن می‌رود تا ظاهر پیام خراب نشود
            if caption:
                caption = caption + "\n\nکاری از: "
            else:
                caption = "کاری از: "
        
        # اضافه کردن امضای نهایی شما در انتهای کپشن
        signature = "\n\n🆔 @tadvin_eslami"
        final_caption = caption + signature
        
        try:
            # فوروارد و ارجاع مستقیم ویدیو (بدون دانلود، بدون آپلود و بدون افت کیفیت)
            await bot.send_message(
                TARGET_CHANNEL_ID, 
                event.message,      # ارسال خود شیء پیام به جای فایل خام برای فعال شدن قابلیت فوروارد بومی تلگرام
                caption=final_caption # جایگذاری کپشن جدید روی ویدیوی فوروارد شده
            )
            print(f"ویدیو با موفقیت و بدون آپلود منتقل شد. شناسه پیام: {message_id}")
        except Exception as e:
            print(f"خطا در ارسال فایل: {e}")

print("ربات هوشمند ضد تکرار و ویرایش کپشن فعال شد!")
bot.run_until_disconnected()
