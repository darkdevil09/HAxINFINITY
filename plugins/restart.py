import os
import sys
from pyrogram import Client, filters
from info import ADMINS

@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def restart_bot(client, message):
    await message.reply_text("🔄 <b>Bot is restarting... Please wait 10-15 seconds.</b>")
    # This replaces the current process with a new one, effectively rebooting the bot natively.
    os.execl(sys.executable, sys.executable, *sys.argv)