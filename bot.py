import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Railway से Token लो
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment!")

# TBomb का पाथ (मान लो कि bomber.py इसी डायरेक्टरी में है)
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
    # Basic validation (10 digits)
    if not phone.isdigit() or len(phone) < 10:
        await update.message.reply_text("❌ Invalid phone number. Use digits only (min 10).")
        return

    # Send "processing" message
    msg = await update.message.reply_text(f"⏳ Sending OTPs to {phone}... (may take 30-60 sec)")

    try:
        # TBomb को बुलाओ – threads बढ़ाकर स्पीड (max 10)
        cmd = [
            "python3", BOMBER_SCRIPT,
            "--phone", phone,
            "--sms",
            "--threads", "10",
            "--timeout", "30"
        ]
        # Async subprocess to avoid blocking
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
            # कोई एरर आया तो भी बॉट क्रैश नहीं होगा
            error_msg = error or "Unknown error (API offline?)"
            await msg.edit_text(
                f"❌ **Failed** to send OTPs.\n"
                f"Reason: `{error_msg[:200]}`\n\n"
                "💡 Tip: TBomb APIs are mostly dead, but bot is alive."
            )
    except Exception as e:
        # हर तरह के एरर को पकड़ो
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
