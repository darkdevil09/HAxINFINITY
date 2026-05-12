from pyrogram import Client, filters, enums
from utils import is_check_admin
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command('manage') & filters.group)
async def members_management(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.')
    
    btn = [[
        InlineKeyboardButton('ᴜɴᴍᴜᴛᴇ ᴀʟʟ', callback_data=f'unmute_all_members'),
        InlineKeyboardButton('ᴜɴʙᴀɴ ᴀʟʟ', callback_data=f'unban_all_members')
    ],[
        InlineKeyboardButton('ᴋɪᴄᴋ ᴍᴜᴛᴇᴅ', callback_data=f'kick_muted_members'),
        InlineKeyboardButton('ᴋɪᴄᴋ ᴅᴇʟᴇᴛᴇᴅ', callback_data=f'kick_deleted_accounts_members')
    ]]
    
    await message.reply_text(
        "<b>ᴍᴇᴍʙᴇʀs ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘᴀɴᴇʟ</b>\n\nsᴇʟᴇᴄᴛ ᴀ ғᴜɴᴄᴛɪᴏɴ ᴛᴏ ᴍᴀɴᴀɢᴇ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs.", 
        reply_markup=InlineKeyboardMarkup(btn)
    )
  
  
@Client.on_message(filters.command('ban') & filters.group)
async def ban_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.')
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
        except IndexError:
            return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ.")
            
    try: user_id = int(user_id)
    except ValueError: pass

    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        user = member.user
    except:
        return await message.reply_text("ᴄᴀɴ'ᴛ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")

    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply_text(f'sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴀɴɴᴇᴅ {user.mention} ғʀᴏᴍ {message.chat.title}')
    except:
        await message.reply_text("ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ʙᴀɴ ᴜsᴇʀs.")


@Client.on_message(filters.command('mute') & filters.group)
async def mute_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.')
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
        except IndexError:
            return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ.")
            
    try: user_id = int(user_id)
    except ValueError: pass

    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        user = member.user
    except:
        return await message.reply_text("ᴄᴀɴ'ᴛ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")

    try:
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
        await message.reply_text(f'sᴜᴄᴄᴇssғᴜʟʟʏ ᴍᴜᴛᴇᴅ {user.mention} ғʀᴏᴍ {message.chat.title}')
    except:
        await message.reply_text("ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴍᴜᴛᴇ ᴜsᴇʀs.")


@Client.on_message(filters.command(["unban", "unmute"]) & filters.group)
async def unban_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.')
    
    cmd = message.command[0].lower()
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
        except IndexError:
            return await message.reply_text(f"ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ {cmd}.")
            
    try: user_id = int(user_id)
    except ValueError: pass

    try:
        user = (await client.get_users(user_id))
    except:
        return await message.reply_text("ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ.")

    try:
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f'sᴜᴄᴄᴇssғᴜʟʟʏ {cmd}ᴇᴅ {user.mention} ғʀᴏᴍ {message.chat.title}')
    except:
        await message.reply_text(f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {cmd} ᴜsᴇʀs.")