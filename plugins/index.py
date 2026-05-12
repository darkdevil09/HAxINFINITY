import re, time, asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import ADMINS, INDEX_EXTENSIONS
from database.ia_filterdb import save_file
from utils import temp, get_readable_time

lock = asyncio.Lock()

# Pre-compile regex for ultra-fast file name cleaning inside loops
CLEAN_REGEX = re.compile(r"@\w+|(_|\-|\.|\+)")

@Client.on_callback_query(filters.regex(r"^index"))
async def index_files(bot, query):
    _, ident, chat, lst_msg_id, skip = query.data.split("#")
    
    if ident == "yes":
        msg = query.message
        await msg.edit_text("📥 ꜱᴛᴀʀᴛɪɴɢ ɪɴᴅᴇxɪɴɢ ᴘʀᴏᴄᴇꜱꜱ...")
        try: chat = int(chat)
        except ValueError: pass
        await index_files_to_db(int(lst_msg_id), chat, msg, bot, int(skip))
        
    elif ident == "cancel":
        temp.CANCEL = True
        await query.message.edit_text("⏹️ ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɪɴᴅᴇxɪɴɢ...")

@Client.on_message(filters.command("index") & filters.private & filters.incoming & filters.user(ADMINS))
async def send_for_index(bot, message):
    if lock.locked():
        return await message.reply_text("⏳ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜꜱ ᴘʀᴏᴄᴇꜱꜱ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.")

    ask = await message.reply_text("📨 ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ʟᴀꜱᴛ ᴄʜᴀɴɴᴇʟ ᴍᴇꜱꜱᴀɢᴇ ᴏʀ ꜱᴇɴᴅ ɪᴛꜱ ʟɪɴᴋ.")
    msg = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    await ask.delete()

    if msg.text and msg.text.startswith("https://t.me"):
        try:
            msg_link = msg.text.split("/")
            last_msg_id = int(msg_link[-1])
            chat_id = msg_link[-2]
            if chat_id.isnumeric(): chat_id = int("-100" + chat_id)
        except Exception:
            return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ ʟɪɴᴋ.")
            
    elif msg.forward_from_chat and msg.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = msg.forward_from_message_id
        chat_id = msg.forward_from_chat.username or msg.forward_from_chat.id
    else:
        return await message.reply_text("❌ ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ᴀ ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ ᴍᴇꜱꜱᴀɢᴇ ᴏʀ ᴠᴀʟɪᴅ ʟɪɴᴋ.")

    try: chat = await bot.get_chat(chat_id)
    except Exception as e: return await message.reply_text(f"❌ ᴇʀʀᴏʀ : <code>{e}</code>")

    if chat.type != enums.ChatType.CHANNEL:
        return await message.reply_text("⚠️ ɪ ᴄᴀɴ ɪɴᴅᴇx ᴏɴʟʏ ᴄʜᴀɴɴᴇʟꜱ.")

    ask_skip = await message.reply_text("🔢 ꜱᴇɴᴅ ꜱᴋɪᴘ ᴍᴇꜱꜱᴀɢᴇ ᴄᴏᴜɴᴛ.")
    msg = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    await ask_skip.delete()

    try: skip = int(msg.text)
    except ValueError: return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ʏᴇꜱ", callback_data=f"index#yes#{chat_id}#{last_msg_id}#{skip}")],
        [InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close_data")]
    ])
    await message.reply_text(
        f"📁 ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɪɴᴅᴇx ᴛʜɪꜱ ᴄʜᴀɴɴᴇʟ?\n\n"
        f"🏷️ ᴄʜᴀɴɴᴇʟ : <b>{chat.title}</b>\n"
        f"📨 ᴛᴏᴛᴀʟ ᴍᴇꜱꜱᴀɢᴇꜱ : <code>{last_msg_id}</code>\n"
        f"⏭️ ꜱᴋɪᴘ : <code>{skip}</code>",
        reply_markup=buttons
    )

async def index_files_to_db(lst_msg_id, chat, msg, bot, skip):
    start_time = time.time()
    last_edit_time = start_time
    total_files, duplicate, errors, deleted, no_media, unsupported, badfiles = 0, 0, 0, 0, 0, 0, 0
    current = skip

    async with lock:
        try:
            async for message in bot.iter_messages(chat, lst_msg_id, skip):
                current += 1
                
                if temp.CANCEL:
                    temp.CANCEL = False
                    time_taken = get_readable_time(time.time() - start_time)
                    return await msg.edit_text(
                        f"⛔ <b>ɪɴᴅᴇxɪɴɢ ᴄᴀɴᴄᴇʟʟᴇᴅ</b>\n\n"
                        f"⏱️ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ : <code>{time_taken}</code>\n\n"
                        f"✅ ꜱᴀᴠᴇᴅ ꜰɪʟᴇꜱ : <code>{total_files}</code>\n"
                        f"♻️ ᴅᴜᴘʟɪᴄᴀᴛᴇ : <code>{duplicate}</code> | 🗑️ ᴅᴇʟᴇᴛᴇᴅ : <code>{deleted}</code>\n"
                        f"📭 ɴᴏɴ ᴍᴇᴅɪᴀ : <code>{no_media}</code> | 🚫 ᴜɴꜱᴜᴘᴘᴏʀᴛᴇᴅ : <code>{unsupported}</code>\n"
                        f"⚠️ ᴇʀʀᴏʀꜱ : <code>{errors}</code> | 📂 ʙᴀᴅ ꜰɪʟᴇꜱ : <code>{badfiles}</code>"
                    )

                # Smart UI Update: Edits message max once every 3 seconds to avoid FloodWait
                if time.time() - last_edit_time > 20:
                    percent = min(100, (current / lst_msg_id) * 100) if lst_msg_id > 0 else 0
                    filled = int(percent / 10)
                    bar = f"[{'█' * filled}{'░' * (10 - filled)}] {percent:.2f}%"
                    btn = InlineKeyboardMarkup([[InlineKeyboardButton("⛔ ᴄᴀɴᴄᴇʟ", callback_data=f"index#cancel#{chat}#{lst_msg_id}#{skip}")]])
                    
                    try:
                        await msg.edit_text(
                            f"📊 <b>ɪɴᴅᴇxɪɴɢ ᴘʀᴏɢʀᴇꜱꜱ</b>\n\n"
                            f"⏳ ᴘʀᴏɢʀᴇꜱꜱ : {bar}\n"
                            f"📨 ᴘʀᴏᴄᴇꜱꜱᴇᴅ : <code>{current} / {lst_msg_id}</code>\n"
                            f"✅ ꜱᴀᴠᴇᴅ : <code>{total_files}</code> | ♻️ ᴅᴜᴘʟɪᴄᴀᴛᴇ : <code>{duplicate}</code>\n"
                            f"🗑️ ᴅᴇʟᴇᴛᴇᴅ : <code>{deleted}</code> | 📭 ɴᴏɴ ᴍᴇᴅɪᴀ : <code>{no_media}</code>\n"
                            f"🚫 ᴜɴꜱᴜᴘᴘᴏʀᴛᴇᴅ : <code>{unsupported}</code> | ⚠️ ᴇʀʀᴏʀꜱ : <code>{errors}</code>",
                            reply_markup=btn
                        )
                        last_edit_time = time.time()
                    except MessageNotModified:
                        pass
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except Exception:
                        pass

                # File Validation Filters
                if message.empty:
                    deleted += 1
                    continue
                if not message.media:
                    no_media += 1
                    continue
                if message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue
                    
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                if not media.file_name:
                    badfiles += 1
                    continue
                if not str(media.file_name).lower().endswith(tuple(INDEX_EXTENSIONS)):
                    unsupported += 1
                    continue

                # Ultra-fast regex cleaning
                media.file_name = CLEAN_REGEX.sub(" ", str(media.file_name))

                # DB Storage
                try:
                    sts = await save_file(media)
                    if sts == "suc": total_files += 1
                    elif sts == "dup": duplicate += 1
                    else: errors += 1
                except Exception:
                    errors += 1

        except Exception as e:
            await msg.edit_text(f"❌ <b>ɪɴᴅᴇxɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ ᴅᴜᴇ ᴛᴏ ᴇʀʀᴏʀ</b>\n\n<code>{e}</code>")
        else:
            time_taken = get_readable_time(time.time() - start_time)
            await msg.edit_text(
                f"✅ <b>ɪɴᴅᴇxɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n"
                f"⏱️ ᴛɪᴍᴇ ᴛᴀᴋᴇɴ : <code>{time_taken}</code>\n\n"
                f"📁 ꜱᴀᴠᴇᴅ ꜰɪʟᴇꜱ : <code>{total_files}</code>\n"
                f"♻️ ᴅᴜᴘʟɪᴄᴀᴛᴇ : <code>{duplicate}</code> | 🗑️ ᴅᴇʟᴇᴛᴇᴅ : <code>{deleted}</code>\n"
                f"📭 ɴᴏɴ ᴍᴇᴅɪᴀ : <code>{no_media}</code> | 🚫 ᴜɴꜱᴜᴘᴘᴏʀᴛᴇᴅ : <code>{unsupported}</code>\n"
                f"⚠️ ᴇʀʀᴏʀꜱ : <code>{errors}</code> | 📂 ʙᴀᴅ ꜰɪʟᴇꜱ : <code>{badfiles}</code>"
            )