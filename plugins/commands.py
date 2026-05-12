import os
import re
import json
import base64
import sys
import pytz
import time
from shortzy import Shortzy
import random, string
import asyncio
from time import time as time_now
import datetime
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, delete_files
from database.users_chats_db import db
from info import INDEX_CHANNELS, ADMINS, IS_VERIFY, VERIFY_TUTORIAL, VERIFY_EXPIRE, TUTORIAL, SHORTLINK_API, SHORTLINK_URL, DELETE_TIME, SUPPORT_LINK, UPDATES_LINK, LOG_CHANNEL, PICS, PROTECT_CONTENT, IS_STREAM, PAYMENT_QR, OWNER_USERNAME, REACTIONS, PM_FILE_DELETE_TIME, OWNER_UPI_ID, VERIFY_LOG_CHANNEL
from utils import get_settings, get_size, is_subscribed, is_check_admin, get_shortlink, get_verify_status, update_verify_status, save_group_settings, temp, get_readable_time, get_wish, get_seconds

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    botid = client.me.id
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        await message.react(emoji="⚡️", big=True)
        
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            username = f'@{message.chat.username}' if message.chat.username else 'Private'
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
            await db.add_chat(message.chat.id, message.chat.title)
        wish = get_wish()
        user = message.from_user.mention if message.from_user else "Dear"
        btn = [[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ ⚡️', url=UPDATES_LINK),
            InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💡', url=SUPPORT_LINK)
        ]]
        await message.reply(text=f"<b>ʜᴇʏ {user}, <i>{wish}</i>\nʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ??</b>", reply_markup=InlineKeyboardMarkup(btn))
        return 
        
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(message.from_user.mention, message.from_user.id))

    verify_status = await get_verify_status(message.from_user.id)
    if verify_status['is_verified'] and datetime.datetime.now() > verify_status['expire_time']:
        await update_verify_status(message.from_user.id, is_verified=False)
    
    if (len(message.command) != 2) or (len(message.command) == 2 and message.command[1] == 'start'):
        buttons = [[
            InlineKeyboardButton("🔰 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🔰", url=f'http://t.me/{temp.U_NAME}?startgroup=start')
        ],[
            InlineKeyboardButton('ℹ️ ᴜᴘᴅᴀᴛᴇꜱ', url=UPDATES_LINK),
            InlineKeyboardButton('🧑‍💻 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('👨‍🚒 ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('📚 ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('✦ ᴄʜᴇᴄᴋ ᴀʟʟ ɢʀᴏᴜᴘꜱ & ᴄʜᴀɴɴᴇʟꜱ ✦', url='https://t.me/hd_movies_hub01/7')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, get_wish()),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    if len(message.command) == 2 and message.command[1] == "plans":
        btn = [            
            [InlineKeyboardButton("🧾 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=OWNER_USERNAME)],
            [InlineKeyboardButton("🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        await message.reply_photo(
            photo=PAYMENT_QR,
            caption=script.PREMIUM_PLAN_TEXT.format(OWNER_UPI_ID),
            reply_markup=reply_markup
        )
        return

    mc = message.command[1]

    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = await get_verify_status(message.from_user.id)
        if verify_status['verify_token'] != token:
            return await message.reply("<b>⚠️ ʏᴏᴜʀ ᴠᴇʀɪꜰʏ ᴛᴏᴋᴇɴ ɪꜱ ɪɴᴠᴀʟɪᴅ.</b>")
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=VERIFY_EXPIRE)
        await update_verify_status(message.from_user.id, is_verified=True, verified_time=time_now(), expire_time=expiry_time)
        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[
                InlineKeyboardButton("🚀 ɢᴇᴛ ᴛʜᴇ ꜰɪʟᴇ ɴᴏᴡ 🚀", url=f'https://t.me/{temp.U_NAME}?start={verify_status["link"]}')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
        await message.reply(
            "✅ <b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟ</b>\n"
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            "🔓 <b>ᴀᴄᴄᴇss ɢʀᴀɴᴛᴇᴅ</b>\n"
            "ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ᴠᴇʀɪꜰɪᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.\n"
            "ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ sᴇʀᴠɪᴄᴇs ᴀʀᴇ ɴᴏᴡ <b>ᴜɴʟᴏᴄᴋᴇᴅ</b>.\n\n"
            "⏱️ <b>sᴇssɪᴏɴ ᴇxᴘɪʀʏ:</b>\n"
            f"└ <code>{get_readable_time(VERIFY_EXPIRE)}</code>\n\n"
            "✨ <b>ᴡʜᴀᴛ's ɴᴇᴡ?</b>\n"
            "• ғᴀsᴛ sᴇᴀʀᴄʜ ᴇɴᴀʙʟᴇᴅ\n"
            "• ᴅɪʀᴇᴄᴛ ғɪʟᴇ sᴛʀᴇᴀᴍɪɴɢ\n"
            "• ɴᴏ ᴍᴏʀᴇ ɪɴᴛᴇʀʀᴜᴘᴛɪᴏɴs\n\n"
            "🚀 <i>ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴇxᴘᴇʀɪᴇɴᴄᴇ!</i>\n"
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>",
            reply_markup=reply_markup,
            protect_content=True
        )
        try:
            tz = pytz.timezone('Asia/Kolkata')
            current_time = datetime.datetime.now(tz).strftime("%I:%M %p - %d %b %Y")
            
            user_name = message.from_user.first_name
            if message.from_user.last_name:
                user_name += f" {message.from_user.last_name}"
                
            log_text = script.VERIFY_LOG_TEXT.format(
                name=user_name,
                id=message.from_user.id,
                time=current_time
            )
            if VERIFY_LOG_CHANNEL and VERIFY_LOG_CHANNEL != 0:
                await client.send_message(chat_id=VERIFY_LOG_CHANNEL, text=log_text, disable_web_page_preview=True)
        except Exception as e:
            print(f"Verification Log Error: {e}")
        return
    
    verify_status = await get_verify_status(message.from_user.id)
    if not await db.has_premium_access(message.from_user.id):
        if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(message.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{temp.U_NAME}?start=verify_{token}')
            btn = [[
                InlineKeyboardButton("🚀 ᴠᴇʀɪꜰʏ ᴛᴏ ᴜɴʟᴏᴄᴋ ꜰɪʟᴇ 🚀", url=link)
            ],[
                InlineKeyboardButton("🗳 ᴛᴜᴛᴏʀɪᴀʟ 🗳", url=VERIFY_TUTORIAL)
            ]]
            await message.reply(
                "⚠️ <b>ᴀᴄᴛɪᴠᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ</b>\n"
                "<b>— — — — — — — — — — — — — — —</b>\n\n"
                "ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇssɪᴏɴ ɪs <b>ɪɴᴀᴄᴛɪᴠᴇ</b>. ᴘʟᴇᴀsᴇ ʀᴇ-ᴠᴇʀɪꜰʏ \n"
                "ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ᴜsɪɴɢ ᴏᴜʀ sᴇʀᴠɪᴄᴇs.\n\n"
                "✨ <b>ᴡʜʏ ᴠᴇʀɪꜰʏ?</b>\n"
                "• ᴜɴʟɪᴍɪᴛᴇᴅ ʜɪɢʜ-sᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅs\n"
                "• ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ғɪʟᴇs\n\n"
                "🚀 <b>sᴛᴇᴘs ᴛᴏ ᴜɴʟᴏᴄᴋ:</b>\n"
                "𝟷. ᴄʟɪᴄᴋ 'ᴠᴇʀɪꜰʏ ɴᴏᴡ' ʙᴇʟᴏᴡ\n"
                "𝟸. ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ sʜᴏʀᴛ sᴇᴄᴜʀɪᴛʏ ᴄʜᴇᴄᴋ\n"
                "𝟹. ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴄᴏɴᴛᴇɴᴛ ɪɴsᴛᴀɴᴛʟʏ!\n\n"
                "📢 <i>ɴᴏᴛᴇ: ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴇxᴘɪʀᴇs ᴇᴠᴇʀʏ 𝟸𝟺 ʜᴏᴜʀs.</i>\n"
                "<b>— — — — — — — — — — — — — — —</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                protect_content=True
            )
            return
            
    settings = await get_settings(int(mc.split("_", 2)[1]))
    if not await db.has_premium_access(message.from_user.id):
        if settings['fsub']:
            btn = await is_subscribed(client, message, settings['fsub'])
            if btn:
                btn.append(
                    [InlineKeyboardButton("🔁 ᴛʀʏ ᴀɢᴀɪɴ 🔁", callback_data=f"checksub#{mc}")]
                )
                reply_markup = InlineKeyboardMarkup(btn)
                await message.reply_photo(
                    photo=random.choice(PICS),
                    caption=f"👋 <b>ʜᴇʟʟᴏ {message.from_user.mention},</b>\n\nᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴍʏ 'ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ' ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ. 😇",
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                return 
        
    if mc.startswith('all'):
        _, grp_id, key = mc.split("_", 2)
        files = temp.FILES.get(key)
        if not files:
            return await message.reply('<b>⚠️ ɴᴏ ꜱᴜᴄʜ ꜰɪʟᴇꜱ ᴇxɪꜱᴛ!</b>')
        settings = await get_settings(int(grp_id))
        file_ids = []
        total_files = await message.reply(f"<b><i>🗂 ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ - <code>{len(files)}</code></i></b>")
        for file in files:
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name=file.file_name,
                file_size=get_size(file.file_size),
            )      
            if settings.get('is_stream', IS_STREAM):
                btn = [[
                    InlineKeyboardButton('🚀 ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ / ᴅᴏᴡɴʟᴏᴀᴅ 🚀', callback_data=f"stream#{file.file_id}")
                ],[
                    InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇꜱ', url=UPDATES_LINK),
                    InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
                ]]
            else:
                btn = [[
                    InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇꜱ', url=UPDATES_LINK),
                    InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
                ]]

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=False if await db.has_premium_access(message.from_user.id) else True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            file_ids.append(msg.id)

        time_str = get_readable_time(PM_FILE_DELETE_TIME)
        vp = await message.reply(f"⚠️ <b>ɴᴏᴛᴇ:</b> ᴛʜᴇꜱᴇ ꜰɪʟᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <b>{time_str}</b> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛꜱ. ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ꜱᴀᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.")
        await asyncio.sleep(PM_FILE_DELETE_TIME)
        buttons = [[InlineKeyboardButton('♻️ ɢᴇᴛ ꜰɪʟᴇꜱ ᴀɢᴀɪɴ ♻️', callback_data=f"get_del_send_all_files#{grp_id}#{key}")]] 
        await client.delete_messages(
            chat_id=message.chat.id,
            message_ids=file_ids + [total_files.id]
        )
        await vp.edit("<b>⚠️ ᴛʜᴇ ꜰɪʟᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ!</b>\nᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴛʜᴇᴍ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(buttons))
        return

    type_, grp_id, file_id = mc.split("_", 2)
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('<b>⚠️ ɴᴏ ꜱᴜᴄʜ ꜰɪʟᴇ ᴇxɪꜱᴛꜱ!</b>')
    files = files_[0]
    settings = await get_settings(int(grp_id))
    
    if type_ != 'shortlink' and settings['shortlink']:
        if not await db.has_premium_access(message.from_user.id):
            link = await get_shortlink(settings['url'], settings['api'], f"https://t.me/{temp.U_NAME}?start=shortlink_{grp_id}_{file_id}")
            btn = [[
                InlineKeyboardButton("♻️ ɢᴇᴛ ꜰɪʟᴇ ♻️", url=link)
            ],[
                InlineKeyboardButton("🔮 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ 🔮", url=settings['tutorial'])
            ]]
            await message.reply(f"📁 <b>[{get_size(files.file_size)}] {files.file_name}</b>\n\nʏᴏᴜʀ ꜰɪʟᴇ ɪꜱ ʀᴇᴀᴅʏ, ᴘʟᴇᴀꜱᴇ ɢᴇᴛ ɪᴛ ᴜꜱɪɴɢ ᴛʜɪꜱ ʟɪɴᴋ. 👍", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
            
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name = files.file_name,
        file_size = get_size(files.file_size),
    )
    if settings.get('is_stream', IS_STREAM):
        btn = [[
            InlineKeyboardButton('🚀 ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ / ᴅᴏᴡɴʟᴏᴀᴅ 🚀', callback_data=f"stream#{file_id}")
        ],[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇꜱ', url=UPDATES_LINK),
            InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
        ]]
    else:
        btn = [[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇꜱ', url=UPDATES_LINK),
            InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
        ]]
        
    vp = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=False if await db.has_premium_access(message.from_user.id) else True,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    time_str = get_readable_time(PM_FILE_DELETE_TIME)
    msg = await vp.reply(f"⚠️ <b>ɴᴏᴛᴇ:</b> ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <b>{time_str}</b> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛꜱ. ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ꜱᴀᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.")
    await asyncio.sleep(PM_FILE_DELETE_TIME)
    btns = [[
        InlineKeyboardButton('♻️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ♻️', callback_data=f"get_del_file#{grp_id}#{file_id}")
    ]]
    await msg.delete()
    await vp.delete()
    await vp.reply("<b>⚠️ ᴛʜᴇ ꜰɪʟᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ!</b>\nᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_message(filters.command('index_channels'))
async def channels_info(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
    ids = INDEX_CHANNELS
    if not ids:
        return await message.reply("<b>⚠️ ɪɴᴅᴇx ᴄʜᴀɴɴᴇʟꜱ ɴᴏᴛ ꜱᴇᴛ.</b>")
    text = '<b>📡 ɪɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟꜱ:</b>\n\n'
    for id in ids:
        chat = await bot.get_chat(id)
        text += f'🔹 {chat.title}\n'
    text += f'\n<b>📊 ᴛᴏᴛᴀʟ:</b> <code>{len(ids)}</code>'
    await message.reply(text)

@Client.on_message(filters.command('stats'))
async def stats(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
    files = await Media.count_documents({})
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    premium = await db.all_premium_users()
    u_size = get_size(await db.get_db_size())
    u_size_int = await db.get_db_size()
    f_size = get_size(536870912 - u_size_int)
    uptime = get_readable_time(time_now() - temp.START_TIME)
    await message.reply_text(script.STATUS_TXT.format(files, users, premium, chats, u_size, f_size, uptime))    
    
@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
        
    settings = await get_settings(grp_id)
    if settings is not None:
        buttons = [[
            InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
            InlineKeyboardButton('✅ ʏᴇꜱ' if settings["auto_filter"] else '♻️ ɴᴏ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
        ],[
            InlineKeyboardButton('ɪᴍᴅʙ ᴘᴏꜱᴛᴇʀ', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
            InlineKeyboardButton('✅ ʏᴇꜱ' if settings["imdb"] else '♻️ ɴᴏ', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
        ],[
            InlineKeyboardButton('ꜱᴘᴇʟʟɪɴɢ ᴄʜᴇᴄᴋ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
            InlineKeyboardButton('✅ ʏᴇꜱ' if settings["spell_check"] else '♻️ ɴᴏ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
        ],[
            InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
            InlineKeyboardButton(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else '♻️ ɴᴏ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
        ],[
            InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ ᴍꜱɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',),
            InlineKeyboardButton('✅ ʏᴇꜱ' if settings["welcome"] else '♻️ ɴᴏ', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}'),
        ],[
            InlineKeyboardButton('ꜱʜᴏʀᴛʟɪɴᴋ', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
            InlineKeyboardButton('✅ ʏᴇꜱ' if settings["shortlink"] else '♻️ ɴᴏ', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
        ],[
            InlineKeyboardButton('ʀᴇꜱᴜʟᴛ ᴘᴀɢᴇ', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}'),
            InlineKeyboardButton('⛓ ʟɪɴᴋ' if settings["links"] else '🧲 ʙᴜᴛᴛᴏɴ', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}')
        ],[
            InlineKeyboardButton('ꜱᴛʀᴇᴀᴍɪɴɢ', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}'),
            InlineKeyboardButton('✅ ᴏɴ' if settings.get("is_stream", IS_STREAM) else '♻️ ᴏꜰꜰ', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}')
        ],[
            InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
        ]]
        await message.reply_text(
            text=f"⚙️ <b>ᴄᴜꜱᴛᴏᴍɪᴢᴇ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ:</b>\n<code>{message.chat.title}</code>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply_text('<b>⚠️ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!</b>')

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
    try:
        template = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>⚠️ ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ!</b>")   
    await save_group_settings(grp_id, 'template', template)
    await message.reply_text(f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴇᴍᴘʟᴀᴛᴇ ꜰᴏʀ <code>{title}</code> ᴛᴏ:</b>\n\n{template}")  
    
@Client.on_message(filters.command('set_caption'))
async def save_caption(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
    try:
        caption = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>⚠️ ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ!</b>") 
    await save_group_settings(grp_id, 'caption', caption)
    await message.reply_text(f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴄᴀᴘᴛɪᴏɴ ꜰᴏʀ <code>{title}</code> ᴛᴏ:</b>\n\n{caption}")
        
@Client.on_message(filters.command('set_shortlink'))
async def save_shortlink(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")    
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
    try:
        _, url, api = message.text.split(" ", 2)
    except:
        return await message.reply_text("<b>⚠️ ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ!</b>\n\n<b>Ex:-</b> <code>/set_shortlink mdisklink.link 5843c3cc...</code>")   
    try:
        await get_shortlink(url, api, f'https://t.me/{temp.U_NAME}')
    except:
        return await message.reply_text("<b>⚠️ ʏᴏᴜʀ ꜱʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ ᴏʀ ᴜʀʟ ɪꜱ ɪɴᴠᴀʟɪᴅ, ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!</b>")   
    await save_group_settings(grp_id, 'url', url)
    await save_group_settings(grp_id, 'api', api)
    await message.reply_text(f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ꜱʜᴏʀᴛʟɪɴᴋ ꜰᴏʀ <code>{title}</code></b>\n\n<b>URL:</b> <code>{url}</code>\n<b>API:</b> <code>{api}</code>")
    
@Client.on_message(filters.command('get_custom_settings'))
async def get_custom_settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')    
    settings = await get_settings(grp_id)
    text = f"""⚙️ <b>ᴄᴜꜱᴛᴏᴍ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ:</b> <code>{title}</code>

🔗 <b>Shortlink URL:</b> <code>{settings["url"]}</code>
🔑 <b>Shortlink API:</b> <code>{settings["api"]}</code>

📝 <b>IMDb Template:</b> <code>{settings['template']}</code>

📁 <b>File Caption:</b> <code>{settings['caption']}</code>

👋 <b>Welcome Text:</b> <code>{settings['welcome_text']}</code>

🗳 <b>Tutorial Link:</b> <code>{settings['tutorial']}</code>

📌 <b>Force Channels:</b> <code>{str(settings['fsub'])[1:-1] if settings['fsub'] else 'Not Set'}</code>"""

    btn = [[
        InlineKeyboardButton(text="🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data")
    ]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

@Client.on_message(filters.command('set_welcome'))
async def save_welcome(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
    try:
        welcome = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>⚠️ ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ!</b>")    
    await save_group_settings(grp_id, 'welcome_text', welcome)
    await message.reply_text(f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍꜱɢ ꜰᴏʀ <code>{title}</code> ᴛᴏ:</b>\n\n{welcome}")
        
@Client.on_message(filters.command('delete'))
async def delete_file(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
    try:
        query = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>⚠️ ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ!</b>\nUsage: <code>/delete [query]</code>")
    msg = await message.reply_text('🔍 <b>ꜱᴇᴀʀᴄʜɪɴɢ...</b>')
    total, files = await delete_files(query)
    if int(total) == 0:
        return await msg.edit('<b>⚠️ ɴᴏ ꜰɪʟᴇꜱ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ ǫᴜᴇʀʏ!</b>')
    btn = [[
        InlineKeyboardButton("✅ ʏᴇꜱ, ᴅᴇʟᴇᴛᴇ", callback_data=f"delete_{query}")
    ],[
        InlineKeyboardButton("🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data")
    ]]
    await msg.edit(f"<b>📊 ᴛᴏᴛᴀʟ <code>{total}</code> ꜰɪʟᴇꜱ ꜰᴏᴜɴᴅ ꜰᴏʀ ǫᴜᴇʀʏ:</b> <code>{query}</code>.\n\n<b>ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛʜᴇᴍ?</b>", reply_markup=InlineKeyboardMarkup(btn))
 
@Client.on_message(filters.command('delete_all'))
async def delete_all_index(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
        
    files = await Media.count_documents({})
    if int(files) == 0:
        return await message.reply_text('<b>⚠️ ɴᴏ ꜰɪʟᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ.</b>')
        
    btn = [[
        InlineKeyboardButton(text="✅ ʏᴇꜱ, ᴅᴇʟᴇᴛᴇ ᴀʟʟ", callback_data="delete_all")
    ],[
        InlineKeyboardButton(text="🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data")
    ]]
    
    await message.reply_text(
        f"<b>⚠️ ᴡᴀʀɴɪɴɢ!\n\nʏᴏᴜ ᴀʀᴇ ᴀʙᴏᴜᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ <code>{files}</code> ꜰɪʟᴇꜱ ꜰʀᴏᴍ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀꜱᴇ.\n\nᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ? ᴛʜɪꜱ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.</b>", 
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_message(filters.command('set_tutorial'))
async def set_tutorial(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")       
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>⚠️ ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ!</b>")   
    await save_group_settings(grp_id, 'tutorial', tutorial)
    await message.reply_text(f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟ ᴄʜᴀɴɢᴇᴅ ᴛᴜᴛᴏʀɪᴀʟ ꜰᴏʀ <code>{title}</code> ᴛᴏ:</b>\n\n{tutorial}")

@Client.on_message(filters.command('ping'))
async def ping(client, message):
    start_time = time.monotonic()
    msg = await message.reply("⚡️")
    end_time = time.monotonic()
    await msg.edit(f'<b>🏓 ᴘᴏɴɢ:</b> <code>{round((end_time - start_time) * 1000)} ms</code>')
    
@Client.on_message(filters.command("add_premium"))
async def give_premium_cmd_handler(client, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
    if len(message.command) == 3:
        user_id = int(message.command[1])
        time = message.command[2]        
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time} 
            await db.update_user(user_data) 
            await message.reply_text(f"✅ <b>ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴜꜱᴇʀ ꜰᴏʀ <code>{time}</code>.</b>")            
            await client.send_message(
                chat_id=user_id,
                text=f"🎉 <b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!</b>\n\n<b>ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰᴏʀ <code>{time}</code> ᴇɴᴊᴏʏ 😀\n</b>",                
            )
        else:
            await message.reply_text("<b>⚠️ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ.</b>\nUse '1day', '1hour', '1min', '1month' or '1year'.")
    else:
        await message.reply_text("<b>⚠️ ᴜꜱᴀɢᴇ:</b> <code>/add_premium [user_id] [time]</code> \n\n<b>Example:</b> <code>/add_premium 1252789 10day</code>")
        
@Client.on_message(filters.command("remove_premium"))
async def remove_premium_cmd_handler(client, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
    if len(message.command) == 2:
        user_id = int(message.command[1])
        time = "1s"
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time}
            await db.update_user(user_data)
            await message.reply_text("✅ <b>ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴜꜱᴇʀ.</b>")
            await client.send_message(
                chat_id=user_id,
                text=f"🚫 <b>ᴘʀᴇᴍɪᴜᴍ ʀᴇᴍᴏᴠᴇᴅ ʙʏ ᴀᴅᴍɪɴꜱ!</b>\n\nᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪꜰ ᴛʜɪꜱ ɪꜱ ᴀ ᴍɪꜱᴛᴀᴋᴇ.\n\n👮 <b>ᴀᴅᴍɪɴ:</b> {OWNER_USERNAME}",
                disable_web_page_preview=True
            )
        else:
            await message.reply_text("<b>⚠️ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ.</b>")
    else:
        await message.reply_text("<b>⚠️ ᴜꜱᴀɢᴇ:</b> <code>/remove_premium [user_id]</code>")
        
@Client.on_message(filters.command("plans"))
async def plans_list(client, message):
    btn = [[
        InlineKeyboardButton("🧾 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=OWNER_USERNAME)
    ],[
        InlineKeyboardButton("🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data")
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    await message.reply_photo(
        photo=PAYMENT_QR,
        caption=script.PREMIUM_PLAN_TEXT.format(OWNER_UPI_ID),
        reply_markup=reply_markup
    )
        
@Client.on_message(filters.command("myplan"))
async def check_plans_cmd(client, message):
    user_id  = message.from_user.id
    if await db.has_premium_access(user_id):        
        remaining_time = await db.check_remaining_uasge(user_id)            
        expiry_time = remaining_time + datetime.datetime.now()
        await message.reply_text(f"🌟 <b>ʏᴏᴜʀ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟꜱ:</b>\n\n⏳ <b>ʀᴇᴍᴀɪɴɪɴɢ ᴛɪᴍᴇ:</b> <code>{remaining_time}</code>\n📅 <b>ᴇxᴘɪʀʏ ᴛɪᴍᴇ:</b> <code>{expiry_time}</code>")
    else:
        btn = [ 
            [InlineKeyboardButton("🎁 ɢᴇᴛ ꜰʀᴇᴇ ᴛʀɪᴀʟ ꜰᴏʀ 5 ᴍɪɴꜱ 🎁", callback_data="get_trail")],
            [InlineKeyboardButton("💎 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ", callback_data="buy_premium")],
            [InlineKeyboardButton("🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        m = await message.reply_sticker("CAACAgIAAxkBAAIBTGVjQbHuhOiboQsDm35brLGyLQ28AAJ-GgACglXYSXgCrotQHjibHgQ")        
        await message.reply_text(f"😢 <b>ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘʀᴇᴍɪᴜᴍ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ.</b>\n\nᴄʜᴇᴄᴋ ᴏᴜᴛ ᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ ᴜꜱɪɴɢ <code>/plans</code>", reply_markup=reply_markup)
        await asyncio.sleep(2)
        await m.delete()

@Client.on_message(filters.private & filters.command("set_pm_search"))
async def set_pm_search(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    try:
        option = (message.text).split(" ", 1)[1].lower()
    except IndexError:
        return await message.reply_text("<b>💔 ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ. ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ 'on' ᴏʀ 'off' / 'true' ᴏʀ 'false' ᴀꜰᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.</b>")
    if option in ['on', 'true']:
        await db.update_pm_search_status(bot_id, enable=True)
        await message.reply_text("✅ <b>ᴘᴍ ꜱᴇᴀʀᴄʜ ᴇɴᴀʙʟᴇᴅ!</b>\nꜰʀᴏᴍ ɴᴏᴡ, ᴜꜱᴇʀꜱ ᴀʀᴇ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇꜱ ɪɴ ʙᴏᴛ ᴘᴍ.")
    elif option in ['off', 'false']:
        await db.update_pm_search_status(bot_id, enable=False)
        await message.reply_text("♻️ <b>ᴘᴍ ꜱᴇᴀʀᴄʜ ᴅɪꜱᴀʙʟᴇᴅ!</b>\nɴᴏ ᴏɴᴇ ɪꜱ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇꜱ ɪɴ ʙᴏᴛ ᴘᴍ.")
    else:
        await message.reply_text("<b>💔 ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ. ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ 'on' ᴏʀ 'off' / 'true' ᴏʀ 'false' ᴀꜰᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.</b>")

@Client.on_message(filters.command('set_fsub'))
async def set_fsub(client, message):
    user_id = message.from_user.id
    if not user_id:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, user_id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
    try:
        ids = message.text.split(" ", 1)[1]
        fsub_ids = list(map(int, ids.split()))
    except IndexError:
        return await message.reply_text("<b>⚠️ ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ!</b>\n\nᴀᴅᴅ ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟꜱ ꜱᴇᴘᴀʀᴀᴛᴇᴅ ʙʏ ꜱᴘᴀᴄᴇꜱ. Like: <code>/set_fsub id1 id2 id3</code>")
    except ValueError:
        return await message.reply_text('<b>⚠️ ᴍᴀᴋᴇ ꜱᴜʀᴇ ɪᴅꜱ ᴀʀᴇ ɪɴᴛᴇɢᴇʀꜱ.</b>')        
    channels = "<b>📡 ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟꜱ:</b>\n"
    for id in fsub_ids:
        try:
            chat = await client.get_chat(id)
        except Exception as e:
            return await message.reply_text(f"⚠️ <code>{id}</code> ɪꜱ ɪɴᴠᴀʟɪᴅ!\nᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ.\n\n<b>Error -</b> <code>{e}</code>")
        if chat.type != enums.ChatType.CHANNEL:
            return await message.reply_text(f"⚠️ <code>{id}</code> ɪꜱ ɴᴏᴛ ᴀ ᴄʜᴀɴɴᴇʟ.")
        channels += f'🔹 {chat.title}\n'
    await save_group_settings(grp_id, 'fsub', fsub_ids)
    await message.reply_text(f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟꜱ ꜰᴏʀ <code>{title}</code> ᴛᴏ:</b>\n\n{channels}")

@Client.on_message(filters.command('remove_fsub'))
async def remove_fsub(client, message):
    grp_id = message.chat.id
    settings = await get_settings(int(grp_id))
    user_id = message.from_user.id
    chat_type = message.chat.type
    if not user_id:
        return await message.reply("<b>⚠️ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.</b>")
    if not await is_check_admin(client, grp_id, user_id):
        return await message.reply_text('<b>⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</b>')
    if not settings['fsub']:
        return await message.reply_text("<b>⚠️ ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅ ᴀɴʏ ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟꜱ.</b>")
    await save_group_settings(grp_id, 'fsub', None)
    await message.reply_text("✅ <b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ʏᴏᴜʀ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ.</b>")

@Client.on_message(filters.command(["del", "delete"]) & filters.private & filters.user(ADMINS))
async def delete_garbage_file(client, message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply_text("⚠️ <b>ʙʜᴀɪ, ᴊɪꜱᴇ ᴅᴇʟᴇᴛᴇ ᴋᴀʀɴᴀ ʜᴀɪ ᴜꜱ ꜰɪʟᴇ (ᴠɪᴅᴇᴏ/ᴅᴏᴄᴜᴍᴇɴᴛ) ᴋᴏ ꜰᴏʀᴡᴀʀᴅ ᴋᴀʀᴏ ᴀᴜʀ ᴜꜱᴘᴇ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ <code>/del</code> ʟɪᴋʜᴏ.</b>")

    media = getattr(message.reply_to_message, message.reply_to_message.media.value, None)
    if not media:
        return await message.reply_text("⚠️ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇᴅɪᴀ! ʏᴇʜ ꜰɪʟᴇ ɴᴀʜɪ ʜᴀɪ.</b>")

    file_id = media.file_id
    file_name = getattr(media, "file_name", "None")
    file_size = getattr(media, "file_size", 0)

    delete_msg = await message.reply_text(f"⏳ <b>ᴅᴇʟᴇᴛɪɴɢ <code>{file_name}</code> ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ...</b>")

    try:
        result = await Media.collection.delete_many({
            "$or": [
                {"_id": file_id},
                {"file_name": file_name, "file_size": file_size}
            ]
        })
        
        if result.deleted_count > 0:
            await delete_msg.edit_text(
                f"✅ <b>ɢᴀʀʙᴀɢᴇ ꜰɪʟᴇ ᴅᴇʟᴇᴛᴇᴅ!</b>\n\n"
                f"🗑 <b>ʀᴇᴍᴏᴠᴇᴅ :</b> <code>{result.deleted_count}</code> ᴍᴀᴛᴄʜɪɴɢ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ᴅʙ.\n"
                f"📁 <b>ɴᴀᴍᴇ :</b> <code>{file_name}</code>\n"
                f"⚖️ <b>ꜱɪᴢᴇ :</b> <code>{get_size(file_size)}</code>"
            )
        else:
            await delete_msg.edit_text("⚠️ <b>ꜰɪʟᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ!</b>\nʏᴇʜ ᴅʙ ᴍᴇɪɴ ᴍᴀᴛᴄʜ ɴᴀʜɪ ʜᴜɪ ʏᴀ ᴘᴇʜʟᴇ ʜɪ ᴅᴇʟᴇᴛᴇ ʜᴏ ᴄʜᴜᴋɪ ʜᴀɪ.")
            
    except Exception as e:
        await delete_msg.edit_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")

@Client.on_message(filters.command("missing") & filters.private & filters.user(ADMINS))
async def view_missing_searches(client, message):
    missed_data = await db.get_top_missed_searches(15)
    
    if not missed_data:
        return await message.reply_text("😎 <b>ᴢᴇʀᴏ ᴍɪꜱꜱɪɴɢ ꜱᴇᴀʀᴄʜᴇꜱ!</b>\nᴛᴜᴍʜᴀʀᴇ ᴜꜱᴇʀꜱ ᴋᴏ ꜱᴀʙ ᴋᴜᴄʜ ᴍɪʟ ʀᴀʜᴀ ʜᴀɪ.")
    
    text = "📈 <b>ᴛᴏᴘ ᴍɪꜱꜱɪɴɢ ꜱᴇᴀʀᴄʜᴇꜱ (ʜɪɢʜ ᴅᴇᴍᴀɴᴅ)</b>\n\n"
    for i, m in enumerate(missed_data, start=1):
        text += f"{i}. <code>{m['query'].title()}</code> - <b>{m['count']}</b> ʀᴇǫᴜᴇꜱᴛꜱ\n"
        
    text += "\n💡 <i>ɪɴ ᴍᴏᴠɪᴇꜱ/ꜱᴇʀɪᴇꜱ ᴋᴏ ᴊᴀʟᴅɪ ɪɴᴅᴇx ᴋᴀʀᴏ ᴛᴀᴀᴋɪ ᴜꜱᴇʀꜱ ᴡᴀᴘᴀꜱ ᴀᴀʏᴇɪɴ!</i>"
    
    btn = [[InlineKeyboardButton("🗑 ᴄʟᴇᴀʀ ʟɪꜱᴛ", callback_data="clear_missing")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^clear_missing$"))
async def clear_missing_cb(client, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!", show_alert=True)
        
    await db.clear_missed_searches()
    await query.answer("✅ ᴍɪꜱꜱɪɴɢ ʟɪꜱᴛ ᴄʟᴇᴀʀᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!", show_alert=True)
    await query.message.edit_text("🗑 <b>ᴍɪꜱꜱɪɴɢ ꜱᴇᴀʀᴄʜᴇꜱ ʟɪꜱᴛ ʜᴀꜱ ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ.</b>")