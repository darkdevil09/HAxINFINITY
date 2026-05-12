import asyncio
from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import SUPPORT_LINK

async def banned_users(_, __, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)

async def disabled_chat(_, __, message: Message):
    return message.chat.id in temp.BANNED_CHATS

disabled_group = filters.create(disabled_chat)

@Client.on_message(filters.private & banned_user & filters.incoming)
async def is_user_banned(bot, message):
    ban = await db.get_ban_status(message.from_user.id)
    buttons = [[
        InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url=SUPPORT_LINK)
    ]]
    
    text = (
        f"⚠️ <b>ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ</b>\n\n"
        f"ʜᴇʟʟᴏ {message.from_user.mention},\n"
        f"ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇsᴛʀɪᴄᴛᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ.\n\n"
        f"🚫 <b>ʀᴇᴀsᴏɴ:</b> <code>{ban['ban_reason']}</code>\n\n"
        f"<i>ɪғ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ, ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ.</i>"
    )
    
    await message.reply(text=text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.group & disabled_group & filters.incoming)
async def is_group_disabled(bot, message):
    chat_info = await db.get_chat(message.chat.id)
    buttons = [[
        InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url=SUPPORT_LINK)
    ]]
    
    text = (
        f"🛑 <b>ᴄʜᴀᴛ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━━━━</b>\n\n"
        f"ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ʙᴇᴇɴ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ʙʏ ᴍʏ ᴏᴡɴᴇʀ. ɪ ᴄᴀɴɴᴏᴛ ᴡᴏʀᴋ ʜᴇʀᴇ ᴀɴʏᴍᴏʀᴇ.\n\n"
        f"📝 <b>ʀᴇᴀsᴏɴ:</b> <code>{chat_info['reason']}</code>\n\n"
        f"👋 <b>ɢᴏᴏᴅʙʏᴇ! ʟᴇᴀᴠɪɴɢ ɪɴ ᴀ ᴍᴏᴍᴇɴᴛ...</b>"
    )
    
    k = await message.reply(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    
    try:
        await k.pin()
    except:
        pass
    await asyncio.sleep(120) 
    await bot.leave_chat(message.chat.id)