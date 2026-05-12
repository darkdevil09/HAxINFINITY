from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, groups_broadcast_messages, temp, get_readable_time
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

lock = asyncio.Lock()

# Visual Progress Bar Function
def get_progress_bar(done, total):
    percentage = (done / total) * 100
    completed = int(percentage / 10)
    bar = "■" * completed + "□" * (10 - completed)
    return f"[{bar}] {round(percentage, 2)}%"

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        await query.message.edit(f"<code>ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</code>")
        temp.USERS_CANCEL = True
    elif ident == 'groups':
        temp.GROUPS_CANCEL = True
        await query.message.edit(f"<code>ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</code>")
               
@Client.on_message(filters.command(["broadcast", "pin_broadcast"]) & filters.user(ADMINS) & filters.reply)
async def users_broadcast(bot, message):
    if lock.locked():
        return await message.reply(f"<code>ᴄᴜʀʀᴇɴᴛʟʏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ, ᴡᴀɪᴛ ғᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇ.</code>")
    pin = True if message.command[0] == 'pin_broadcast' else False
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text=f"<code>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ᴜsᴇʀs ᴍᴇssᴀɢᴇs...</code>")
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0

    async with lock:
        async for user in users:
            time_taken = get_readable_time(time.time()-start_time)
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                await b_sts.edit(f"💠 <b>ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ</b>\n\n⌛ <b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{time_taken}</code>\n📊 <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>\n✅ <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ғᴀɪʟᴇᴅ:</b> <code>{failed}</code>")
                return
            sts = await broadcast_messages(int(user['id']), b_msg, pin)
            if sts == 'Success': success += 1
            elif sts == 'Error': failed += 1
            done += 1
            if not done % 80:
                p_bar = get_progress_bar(done, total_users)
                btn = [[InlineKeyboardButton('🚫 ᴄᴀɴᴄᴇʟ', callback_data=f'broadcast_cancel#users')]]
                await b_sts.edit(f"🚀 <b>ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n📶 <b>ᴘʀᴏɢʀᴇss:</b> <code>{p_bar}</code>\n📊 <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_users}</code>\n✅ <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ғᴀɪʟᴇᴅ:</b> <code>{failed}</code>", reply_markup=InlineKeyboardMarkup(btn))
        
        await b_sts.edit(f"✅ <b>ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n⌛ <b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{time_taken}</code>\n📊 <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>\n✅ <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ғᴀɪʟᴇᴅ:</b> <code>{failed}</code>")


@Client.on_message(filters.command(["grp_broadcast", "pin_grp_broadcast"]) & filters.user(ADMINS) & filters.reply)
async def groups_broadcast(bot, message):
    if lock.locked():
        return await message.reply(f"<code>ᴄᴜʀʀᴇɴᴛʟʏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ, ᴡᴀɪᴛ ғᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇ.</code>")
    pin = True if message.command[0] == 'pin_grp_broadcast' else False
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text=f"<code>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘs ᴍᴇssᴀɢᴇs...</code>")
    start_time = time.time()
    total_chats = await db.total_chat_count()
    done = 0
    failed = 0
    success = 0

    async with lock:
        async for chat in chats:
            time_taken = get_readable_time(time.time()-start_time)
            if temp.GROUPS_CANCEL:
                temp.GROUPS_CANCEL = False
                await b_sts.edit(f"💠 <b>ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ</b>\n\n⌛ <b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{time_taken}</code>\n📊 <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs:</b> <code>{total_chats}</code>\n✅ <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ғᴀɪʟᴇᴅ:</b> <code>{failed}</code>")
                return
            sts = await groups_broadcast_messages(int(chat['id']), b_msg, pin)
            if sts == 'Success': success += 1
            elif sts == 'Error': failed += 1
            done += 1
            if not done % 20:
                p_bar = get_progress_bar(done, total_chats)
                btn = [[InlineKeyboardButton('🚫 ᴄᴀɴᴄᴇʟ', callback_data=f'broadcast_cancel#groups')]]
                await b_sts.edit(f"🚀 <b>ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n📶 <b>ᴘʀᴏɢʀᴇss:</b> <code>{p_bar}</code>\n📊 <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_chats}</code>\n✅ <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ғᴀɪʟᴇᴅ:</b> <code>{failed}</code>", reply_markup=InlineKeyboardMarkup(btn))    
        
        await b_sts.edit(f"✅ <b>ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n⌛ <b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{time_taken}</code>\n📊 <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs:</b> <code>{total_chats}</code>\n✅ <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ғᴀɪʟᴇᴅ:</b> <code>{failed}</code>")