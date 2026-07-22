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
        # सही कमांड – बिना --phone, --threads, --timeout
        cmd = [
            "python3", "bomber.py",
            phone,           # positional argument
            "--sms"          # SMS mode
            # अगर call भी चाहिए तो --call डाल देना
        ]
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
            response += f"📝 Output:\n`{output[:300]}`" if output else "No output."
            await msg.edit_text(response, parse_mode='Markdown')
        else:
            error_msg = error or "Unknown error (API offline?)"
            await msg.edit_text(
                f"❌ **Failed** to send OTPs.\n"
                f"Reason: `{error_msg[:200]}`\n\n"
                "💡 Tip: APIs may be dead, but bot is alive."
            )
    except Exception as e:
        await msg.edit_text(f"⚠️ Unexpected error: `{str(e)[:200]}`\nBut bot is still running.")
