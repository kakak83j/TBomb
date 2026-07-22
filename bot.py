import os
import re
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===================== CONFIG =====================
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN environment variable not set!")

# ===================== HELPERS =====================
def mask_phone(phone: str) -> str:
    """सिर्फ आखिरी 2 अंक दिखाएं, बाकी छिपाएं"""
    if len(phone) <= 2:
        return "***"
    return phone[:-2] + "XX"

def mock_send_sms(phone: str) -> tuple:
    """
    यह फंक्शन असली SMS नहीं भेजता (क्योंकि APIs मर चुकी हैं)।
    बस एक मॉक रिस्पॉन्स देता है ताकि बॉट क्रैश न हो।
    """
    # कुछ रैंडम डिले (जैसे नेटवर्क कॉल)
    # asyncio.sleep(2)  # चाहे तो अनकमेंट करके रियलिस्टिक बनाओ
    return True, f"[MOCK] SMS would be sent to {mask_phone(phone)} (API offline)"

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 **TBomb Bot (Standalone)**\n"
        "Usage: `/bomb <phone>`\n"
        "Example: `/bomb 9876543210`\n\n"
        "⚠️ Note: This is a mock – no real SMS will be sent.\n"
        "But the bot works without errors!"
    )

async def bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1️⃣ Check if number provided
    if not context.args:
        await update.message.reply_text("❌ Please provide phone number.\nUsage: `/bomb 9876543210`")
        return

    phone = context.args[0].strip()
    if not phone.isdigit() or len(phone) < 10:
        await update.message.reply_text("❌ Invalid number. Use digits only (min 10).")
        return

    masked = mask_phone(phone)
    msg = await update.message.reply_text(f"⏳ Sending OTPs to {masked}...")

    try:
        # 2️⃣ Call the mock function (no external script needed)
        success, result = await asyncio.to_thread(mock_send_sms, phone)

        if success:
            response = f"✅ **Success!** OTPs sent to {masked}\n📝 {result}"
            await msg.edit_text(response, parse_mode='Markdown')
        else:
            # कभी fail नहीं होगा, पर फिर भी हैंडल कर लिया
            await msg.edit_text(f"❌ Failed to send to {masked}.\nReason: {result}")
    except Exception as e:
        # 3️⃣ किसी भी अनपेक्षित एरर को पकड़ो
        error_msg = str(e)[:200]
        await msg.edit_text(f"⚠️ Unexpected error: `{error_msg}`\nBot is still alive.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is healthy and running.")

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb))
    app.add_handler(CommandHandler("status", status))
    print("🤖 TBomb Bot (standalone) started. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
