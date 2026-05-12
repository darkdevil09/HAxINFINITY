import os
import logging
import asyncio
from datetime import datetime
from speedtest import Speedtest, ConfigRetrievalError
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty

from info import ADMINS
from utils import get_size

@Client.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type
    replied_to_msg = message.reply_to_message
    
    if replied_to_msg:
        fwd = replied_to_msg.forward_from_chat or replied_to_msg.chat
        title = getattr(fwd, "title", "ᴛʜɪs ᴄʜᴀᴛ")
        return await message.reply_text(f"✨ ᴄʜᴀᴛ ɪᴅ ᴏғ <b>{title}</b>: <code>{fwd.id}</code>")

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f"👤 ʏᴏᴜʀ ᴜsᴇʀ ɪᴅ: <code>{message.from_user.id}</code>")

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f"👥 ᴛʜɪs ɢʀᴏᴜᴘ ɪᴅ: <code>{message.chat.id}</code>")

    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f"📢 ᴛʜɪs ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{message.chat.id}</code>")


@Client.on_message(filters.command('speedtest') & filters.user(ADMINS))
async def speedtest(client, message):
    msg = await message.reply_text(f"🚀 <code>ɪɴɪᴛɪᴀᴛɪɴɢ sᴘᴇᴇᴅᴛᴇsᴛ...</code>")
    try:
        speed = Speedtest()
        speed.get_best_server()
    except ConfigRetrievalError:
        return await msg.edit(f"❌ <code>ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴇʀʀᴏʀ... ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!</code>")
    
    await msg.edit(f"⬇️ <code>ᴛᴇsᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ sᴘᴇᴇᴅ...</code>")
    speed.download()
    
    await msg.edit(f"⬆️ <code>ᴛᴇsᴛɪɴɢ ᴜᴘʟᴏᴀᴅ sᴘᴇᴇᴅ...</code>")
    speed.upload()
    
    speed.results.share()
    result = speed.results.dict()
    photo = result['share']
    
    # Direct Small Caps UI
    text = f'''
💠 <b>ɴᴇᴛᴡᴏʀᴋ sᴛᴀᴛɪsᴛɪᴄs</b>
<b>━━━━━━━━━━━━━━━━━━━━━</b>
🚀 <b>ᴅᴏᴡɴʟᴏᴀᴅ:</b> <code>{get_size(result['download'])}/s</code>
📤 <b>ᴜᴘʟᴏᴀᴅ:</b> <code>{get_size(result['upload'])}/s</code>
📡 <b>ᴘɪɴɢ:</b> <code>{result['ping']} ms</code>
⏰ <b>ᴛɪᴍᴇ:</b> <code>{datetime.strptime(result['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%I:%M %p")}</code>
📊 <b>ᴛᴏᴛᴀʟ ᴅᴀᴛᴀ:</b> <code>{get_size(int(result['bytes_sent']) + int(result['bytes_received']))}</code>

🛰 <b>sᴇʀᴠᴇʀ ᴅᴇᴛᴀɪʟs</b>
<b>━━━━━━━━━━━━━━━━━━━━━</b>
🏢 <b>sᴘᴏɴsᴏʀ:</b> <code>{result['server']['sponsor']}</code>
📍 <b>ʟᴏᴄᴀᴛɪᴏɴ:</b> <code>{result['server']['name']}, {result['server']['country']}</code>

👤 <b>ᴄʟɪᴇɴᴛ ɪɴғᴏ</b>
<b>━━━━━━━━━━━━━━━━━━━━━</b>
🌐 <b>ɪᴘ ᴀᴅᴅʀᴇss:</b> <code>{result['client']['ip']}</code>
🗼 <b>ɪsᴘ:</b> <code>{result['client']['isp']}</code>
<b>━━━━━━━━━━━━━━━━━━━━━</b>
<i>#ɪɴғɪɴɪᴛʏ_sᴘᴇᴇᴅᴛᴇsᴛ</i>
'''
    try:
        await message.reply_photo(photo=photo, caption=text)
        await msg.delete()
    except Exception:
        await msg.edit(text)