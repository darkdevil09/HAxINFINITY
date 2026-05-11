import random
import asyncio
import re
from time import time as time_now
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from datetime import datetime, timedelta
import pyrogram
from info import ADMINS, URL, MAX_BTN, BIN_CHANNEL, IS_STREAM, DELETE_TIME, FILMS_LINK, IS_VERIFY, VERIFY_EXPIRE, LOG_CHANNEL, SUPPORT_GROUP, SUPPORT_LINK, UPDATES_LINK, PICS, PROTECT_CONTENT, IMDB, AUTO_FILTER, SPELL_CHECK, IMDB_TEMPLATE, AUTO_DELETE, LANGUAGES, PAYMENT_QR, QUALITY, OWNER_UPI_ID, OWNER_USERNAME
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, WebAppInfo
from pyrogram import Client, filters, enums
from utils import get_size, is_subscribed, is_check_admin, get_wish, get_shortlink, get_verify_status, update_verify_status, get_readable_time, get_poster, temp, get_settings, save_group_settings, smart_query_parser
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, delete_files, get_dynamic_filters

BUTTONS = {}
CAP = {}

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    bot_id = client.me.id
    files, n_offset, total = await get_search_results(message.text)
    btn = [[InlineKeyboardButton("🗂 ᴄʟɪᴄᴋ ʜᴇʀᴇ 🗂", url=FILMS_LINK)]]
    reply_markup = InlineKeyboardMarkup(btn)
    
    if await db.get_pm_search_status(bot_id):
        s = await message.reply(f"<b><i>🔍 ꜱᴇᴀʀᴄʜɪɴɢ ꜰᴏʀ '<code>{message.text}</code>'...</i></b>", quote=True)
        await auto_filter(client, message, s)
    else:
        if int(total) != 0:
            await message.reply_text(f'<b><i>🤗 ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ 👇</i></b>', reply_markup=reply_markup)
        else:
            await message.reply_text(f'<b><i>📢 ꜱᴇɴᴅ ᴍᴏᴠɪᴇ ᴏʀ ꜱᴇʀɪᴇꜱ ʀᴇǫᴜᴇꜱᴛ ʜᴇʀᴇ 👇</i></b>', reply_markup=reply_markup)

@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
    try:
        client_id = (await client.get_me()).id
        vp = await client.get_chat_member(message.chat.id, client_id)
        if not vp.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return
    except: return
        
    if not await db.get_chat(message.chat.id):
        total = int(message.chat.members_count)
        username = f'@{message.chat.username}' if message.chat.username else vp.invite_link
        await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
        await db.add_chat(message.chat.id, message.chat.title)
        
    chat_id = message.chat.id
    settings = await get_settings(chat_id)
    user_id = message.from_user.id if message and message.from_user else 0
    
    if settings["auto_filter"]:
        if not user_id:
            await message.reply("<b>ɪ'ᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ꜰᴏʀ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ! 🥷</b>")
            return
            
        if message.chat.id == SUPPORT_GROUP:
            files, offset, total = await get_search_results(message.text)
            if files:
                btn = [[InlineKeyboardButton("🗂 ᴄʟɪᴄᴋ ʜᴇʀᴇ 🗂", url=FILMS_LINK)]]
                await message.reply_text(f'<b>ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ 👇</b>', reply_markup=InlineKeyboardMarkup(btn))
            return
            
        if message.text.startswith("/"): return
            
        elif '@admin' in message.text.lower() or '@admins' in message.text.lower():
            if await is_check_admin(client, message.chat.id, message.from_user.id): return
            admins = []
            async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not member.user.is_bot:
                    admins.append(member.user.id)
                    if member.status == enums.ChatMemberStatus.OWNER:
                        if message.reply_to_message:
                            try:
                                sent_msg = await message.reply_to_message.forward(member.user.id)
                                await sent_msg.reply_text(f"#ᴀᴛᴛᴇɴᴛɪᴏɴ\n★ ᴜꜱᴇʀ: {message.from_user.mention}\n★ ɢʀᴏᴜᴘ: {message.chat.title}\n\n★ <a href={message.reply_to_message.link}>ɢᴏ ᴛᴏ ᴍᴇꜱꜱᴀɢᴇ</a>", disable_web_page_preview=True)
                            except: pass
                        else:
                            try:
                                sent_msg = await message.forward(member.user.id)
                                await sent_msg.reply_text(f"#ᴀᴛᴛᴇɴᴛɪᴏɴ\n★ ᴜꜱᴇʀ: {message.from_user.mention}\n★ ɢʀᴏᴜᴘ: {message.chat.title}\n\n★ <a href={message.link}>ɢᴏ ᴛᴏ ᴍᴇꜱꜱᴀɢᴇ</a>", disable_web_page_preview=True)
                            except: pass
            hidden_mentions = (f'[\u2064](tg://user?id={user_id})' for user_id in admins)
            await message.reply_text('<b>ʀᴇᴘᴏʀᴛ ꜱᴇɴᴛ! ✅</b>' + ''.join(hidden_mentions))
            return

        elif re.findall(r'https?://\S+|www\.\S+|t\.me/\S+|@\w+', message.text):
            if await is_check_admin(client, message.chat.id, message.from_user.id): return
            await message.delete()
            return await message.reply('<b>ʟɪɴᴋꜱ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ʜᴇʀᴇ! 🚫</b>')
        
        elif '#request' in message.text.lower():
            if message.from_user.id in ADMINS: return
            await client.send_message(LOG_CHANNEL, f"#Request\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ Message: {re.sub(r'#request', '', message.text.lower())}")
            await message.reply_text("<b>ʀᴇǫᴜᴇꜱᴛ ꜱᴇɴᴛ! ✅</b>")
            return  
        else:
            s = await message.reply(f"<b><i>🔍 ꜱᴇᴀʀᴄʜɪɴɢ ꜰᴏʀ '<code>{message.text}</code>'...</i></b>")
            await auto_filter(client, message, s)
    else:
        k = await message.reply_text('<b>ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ ᴏꜰꜰ! ♻️</b>')
        await asyncio.sleep(5)
        await k.delete()
        try: await message.delete()
        except: pass

async def auto_filter(client, msg, s, spoll_state=None):
    try:
        req = msg.from_user.id if msg and msg.from_user else 0
        key = f"{msg.chat.id}-{msg.id}"
        settings = await get_settings(msg.chat.id)

        if not spoll_state:
            raw_search = msg.text
            clean_search, locks = smart_query_parser(raw_search)
            
            temp.SEARCH_STATE[key] = {
                'query': clean_search,
                'locks': locks,
                'offset': 0
            }
            files, offset, total_results = await get_search_results(clean_search, offset=0, locks=locks)
            
            if not files:
                if settings["spell_check"]:
                    await advantage_spell_chok(msg, s)
                else:
                    try:
                        k = await s.edit_text(f"<b>⚠️ ɴᴏ ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ ꜰᴏʀ <code>{raw_search}</code>.</b>")
                        await asyncio.sleep(10)
                        await k.delete()
                    except Exception:
                        await s.delete() 
                    try: await msg.delete()
                    except: pass
                return
        else:
            clean_search = spoll_state['query']
            locks = spoll_state['locks']
            offset_val = int(spoll_state.get('offset', 0)) if spoll_state.get('offset') else 0
            files, offset, total_results = await get_search_results(clean_search, offset=offset_val, locks=locks)
            temp.SEARCH_STATE[key] = spoll_state
            
        temp.FILES[key] = files
        BUTTONS[key] = clean_search
        
        has_seasons = False
        for f in files:
            if re.search(r'\b(?:s|season\s?)(\d{1,2})\b', f.file_name.lower()):
                has_seasons = True
                break
        
        files_link = ""
        if settings['links']:
            btn = []
            for file_num, file in enumerate(files, start=1):
                files_link += f"""<b>\n\n♻️{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{msg.chat.id}_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>"""
        else:
            btn = [[InlineKeyboardButton(text=f"📂 {get_size(file.file_size)} {file.file_name}", callback_data=f'file#{file.file_id}')] for file in files]   
            
        filter_row_1 = []
        if locks.get('lang'): filter_row_1.append(InlineKeyboardButton(f"✅ {locks['lang'].upper()}", callback_data=f"clear#lang#{key}"))
        else: filter_row_1.append(InlineKeyboardButton("ʟᴀɴɢ", callback_data=f"menu#lang#{key}"))
        
        if locks.get('qual'): filter_row_1.append(InlineKeyboardButton(f"✅ {locks['qual'].upper()}", callback_data=f"clear#qual#{key}"))
        else: filter_row_1.append(InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"menu#qual#{key}"))
            
        if locks.get('year'): filter_row_1.append(InlineKeyboardButton(f"✅ {locks['year']}", callback_data=f"clear#year#{key}"))
        else: filter_row_1.append(InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"menu#year#{key}"))

        filter_row_2 = []
        get_all_data = f"https://t.me/{temp.U_NAME}?start=all_{msg.chat.id}_{key}" if settings['shortlink'] and not await db.has_premium_access(req) else f"send_all#{key}#{req}"
        filter_row_2.append(InlineKeyboardButton("ɢᴇᴛ ᴀʟʟ", url=get_all_data) if get_all_data.startswith("http") else InlineKeyboardButton("ɢᴇᴛ ᴀʟʟ", callback_data=get_all_data))
        
        if has_seasons or locks.get('season'):
            if locks.get('season'):
                if locks.get('episode'): filter_row_2.append(InlineKeyboardButton(f"✅ ᴇ{locks['episode']}", callback_data=f"clear#episode#{key}"))
                else:
                    filter_row_2.append(InlineKeyboardButton(f"✅ ꜱ{locks['season']}", callback_data=f"clear#season#{key}"))
                    filter_row_2.append(InlineKeyboardButton("ᴇᴘɪꜱᴏᴅᴇꜱ", callback_data=f"menu#episode#{key}"))
            else:
                filter_row_2.append(InlineKeyboardButton("ꜱᴇᴀꜱᴏɴꜱ", callback_data=f"menu#season#{key}"))
                
        filter_row_2.append(InlineKeyboardButton("ʙᴜʏ", url=f"https://t.me/{temp.U_NAME}?start=plans"))

        btn.insert(0, filter_row_1)
        btn.insert(1, filter_row_2)

        if offset != "":
            current_page = math.ceil(int(spoll_state.get('offset', 0)) / MAX_BTN) + 1 if spoll_state else 1
            btn.append([
                InlineKeyboardButton(text=f"{current_page}/{math.ceil(total_results / MAX_BTN)}", callback_data="buttons"),
                InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}")
            ])
                
        imdb = await get_poster(clean_search, file=(files[0]).file_name) if settings["imdb"] else None
        TEMPLATE = settings['template']
        
        filter_status = ""
        active_filters = [str(v).upper() for k,v in locks.items() if v]
        if active_filters:
            filter_status = f"\n🚦 <b>ꜰɪʟᴛᴇʀꜱ:</b> " + " | ".join(active_filters)
        
        if imdb:
            cap = TEMPLATE.format(
                query=clean_search, title=imdb['title'], votes=imdb['votes'], aka=imdb["aka"],
                seasons=imdb["seasons"], box_office=imdb['box_office'], localized_title=imdb['localized_title'],
                kind=imdb['kind'], imdb_id=imdb["imdb_id"], cast=imdb["cast"], runtime=imdb["runtime"],
                countries=imdb["countries"], certificates=imdb["certificates"], languages=imdb["languages"],
                director=imdb["director"], writer=imdb["writer"], producer=imdb["producer"],
                composer=imdb["composer"], cinematographer=imdb["cinematographer"], music_team=imdb["music_team"],
                distributors=imdb["distributors"], release_date=imdb['release_date'], year=imdb['year'],
                genres=imdb['genres'], poster=imdb['poster'], plot=imdb['plot'], rating=imdb['rating'],
                url=imdb['url'], **locals()
            )
        else:
            cap = f"<b>💭 ʜᴇʏ {msg.from_user.mention},\n♻️ ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ ꜱᴇᴀʀᴄʜ <code>{clean_search}</code>...</b>"
            
        cap += filter_status
        CAP[key] = cap
        del_msg = f"\n\n<blockquote><b>⚠️ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪꜱꜱᴜᴇꜱ</b></blockquote>" if settings["auto_delete"] else ''
        
        if imdb and imdb.get('poster'):
            try: await s.delete() 
            except: pass
            try:
                k = await msg.reply_photo(photo=imdb.get('poster'), caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
                if settings["auto_delete"]:
                    await asyncio.sleep(DELETE_TIME)
                    await k.delete()
                    try: await msg.delete()
                    except: pass
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                k = await msg.reply_photo(photo=poster, caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
                if settings["auto_delete"]:
                    await asyncio.sleep(DELETE_TIME)
                    await k.delete()
                    try: await msg.delete()
                    except: pass
            except Exception as e:
                k = await msg.reply_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, quote=True)
                if settings["auto_delete"]:
                    await asyncio.sleep(DELETE_TIME)
                    await k.delete()
                    try: await msg.delete()
                    except: pass
        else:
            try:
                k = await s.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
                if settings["auto_delete"]:
                    await asyncio.sleep(DELETE_TIME)
                    await k.delete()
                    try: await msg.delete()
                    except: pass
            except Exception as e:
                try: await s.delete()
                except: pass
                if "MESSAGE_NOT_MODIFIED" not in str(e):
                    try:
                        k = await msg.reply_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, quote=True)
                        if settings["auto_delete"]:
                            await asyncio.sleep(DELETE_TIME)
                            await k.delete()
                            try: await msg.delete()
                            except: pass
                    except: pass

    except Exception as e:
        try: await s.delete()
        except: pass
        print(f"Auto Filter Exception: {e}")

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇꜱᴜʟᴛꜱ!", show_alert=True)
        
    state = temp.SEARCH_STATE.get(key)
    if not state: return await query.answer("ꜱᴇᴀʀᴄʜ ᴄᴏɴᴛᴇxᴛ ᴇxᴘɪʀᴇᴅ!", show_alert=True)
    
    state['offset'] = offset
    await auto_filter(bot, query.message.reply_to_message, query.message, spoll_state=state)

@Client.on_callback_query(filters.regex(r"^(menu|apply|clear)#(lang|qual|year|season|episode)"))
async def universal_filter_router(client, query):
    parts = query.data.split("#")
    action, f_type = parts[0], parts[1]
    
    if action == "apply":
        val, key = parts[2], parts[3]
    else:
        key = parts[2]
        
    state = temp.SEARCH_STATE.get(key)
    if not state:
        return await query.answer("ꜱᴇᴀʀᴄʜ ᴄᴏɴᴛᴇxᴛ ᴇxᴘɪʀᴇᴅ!", show_alert=True)
        
    if action == "menu":
        avail = await get_dynamic_filters(state['query'], state['locks'], f_type)
        if not avail:
            return await query.answer(f"ɴᴏ ᴏᴘᴛɪᴏɴꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ʜᴇʀᴇ.", show_alert=True)
        
        btn = []
        for i in range(0, len(avail), 3):
            row = []
            for item in avail[i:i+3]:
                display_text = item.upper() if f_type == 'qual' else (f"ꜱ{item}" if f_type == 'season' else (f"ᴇ{item}" if f_type == 'episode' else item.upper()))
                row.append(InlineKeyboardButton(text=display_text, callback_data=f"apply#{f_type}#{item}#{key}"))
            btn.append(row)
        
        btn.append([InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"next_0_{key}_{state.get('offset', 0)}")])
        await query.message.edit_text(f"<b>ꜱᴇʟᴇᴄᴛ ꜰɪʟᴛᴇʀ:</b>", reply_markup=InlineKeyboardMarkup(btn))
        return
        
    elif action == "apply":
        state['locks'][f_type] = val
    elif action == "clear":
        state['locks'][f_type] = None
        if f_type == "season": state['locks']['episode'] = None 
        
    state['offset'] = 0 
    await query.answer("ꜰɪʟᴛᴇʀ ᴜᴘᴅᴀᴛᴇᴅ!")
    await auto_filter(client, query.message.reply_to_message, query.message, spoll_state=state)

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇꜱᴜʟᴛꜱ!", show_alert=True)
    movie = await get_poster(id, id=True)
    search = movie.get('title')
    s = await query.message.edit_text(f"<b><i>🔍 ᴄʜᴇᴄᴋɪɴɢ '<code>{search}</code>' ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ...</i></b>")
    await query.answer('')
    state = {'query': search, 'locks': {'lang': None, 'qual': None, 'season': None, 'episode': None, 'year': None}, 'offset': 0}
    await auto_filter(bot, query.message.reply_to_message, s, spoll_state=state)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
        await query.answer("ᴄʟᴏꜱᴇᴅ!")
        await query.message.delete()
        try: await query.message.reply_to_message.delete()
        except: pass
  
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        try: user = query.message.reply_to_message.from_user.id
        except: user = query.message.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇꜱᴜʟᴛꜱ!", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file_id}")

    elif query.data.startswith("get_del_file"):
        ident, group_id, file_id = query.data.split("#")
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{group_id}_{file_id}")
        await query.message.delete()

    elif query.data.startswith("get_del_send_all_files"):
        ident, group_id, key = query.data.split("#")
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{group_id}_{key}")
        await query.message.delete()
        
    elif query.data.startswith("stream"):
        file_id = query.data.split('#', 1)[1]
        msg = await client.send_cached_media(chat_id=BIN_CHANNEL, file_id=file_id)
        watch = f"{URL}watch/{msg.id}"
        download = f"{URL}download/{msg.id}"
        btn=[
            [InlineKeyboardButton("ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ", url=watch), InlineKeyboardButton("ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download)],
            [InlineKeyboardButton("ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ", web_app=WebAppInfo(url=watch))],
            [InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close_data')]
        ]
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    
    elif query.data == "get_trail":
        user_id = query.from_user.id
        free_trial_status = await db.get_free_trial_status(user_id)
        if not free_trial_status:            
            await db.give_free_trail(user_id)
            await query.message.edit_text("**ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ ꜰʀᴇᴇ ᴛʀᴀɪʟ ꜰᴏʀ 5 ᴍɪɴᴜᴛᴇꜱ ꜰʀᴏᴍ ɴᴏᴡ 😀**")
            return
        else:
            await query.message.edit_text("**🤣 ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ ꜰʀᴇᴇ ᴛʀᴀɪʟ. ɴᴏᴡ ɴᴏ ᴍᴏʀᴇ ꜰʀᴇᴇ ᴛʀᴀɪʟꜱ.**")
            return
                
    elif query.data.startswith("checksub"):
        ident, mc = query.data.split("#")
        settings = await get_settings(int(mc.split("_", 2)[1]))
        btn = await is_subscribed(client, query, settings['fsub'])
        if btn:
            await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ.", show_alert=True)
            btn.append([InlineKeyboardButton("ᴛʀʏ ᴀɢᴀɪɴ", callback_data=f"checksub#{mc}")])
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
            return
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={mc}")
        await query.message.delete()

    elif query.data.startswith("unmuteme"):
        ident, userid = query.data.split("#")
        user_id = query.from_user.id
        settings = await get_settings(int(query.message.chat.id))
        if userid == 0:
            return await query.answer("ʏᴏᴜ ᴀʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!", show_alert=True)
        if userid != user_id:
            return await query.answer("ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ ☠️", show_alert=True)
        btn = await is_subscribed(client, query, settings['fsub'])
        if btn:
           await query.answer("ᴋɪɴᴅʟʏ ᴊᴏɪɴ ɢɪᴠᴇɴ ᴄʜᴀɴɴᴇʟ ᴛᴏ ɢᴇᴛ ᴜɴᴍᴜᴛᴇ", show_alert=True)
        else:
            await client.unban_chat_member(query.message.chat.id, user_id)
            await query.answer("ᴜɴᴍᴜᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!", show_alert=True)
            try: await query.message.delete()
            except: return
   
    elif query.data == "buttons":
        await query.answer("⚠️")

    elif query.data == "instructions":
        await query.answer("ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ...\nᴇxᴀᴍᴘʟᴇ:\nʙʟᴀᴄᴋ ᴀᴅᴀᴍ ᴏʀ ʙʟᴀᴄᴋ ᴀᴅᴀᴍ 2022\n\nᴛᴠ ꜱᴇʀɪᴇꜱ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ...\nᴇxᴀᴍᴘʟᴇ:\nʟᴏᴋɪ ꜱ01ᴇ01 ᴏʀ ʟᴏᴋɪ ꜱ01 ᴇ01", show_alert=True)

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton("ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'http://t.me/{temp.U_NAME}?startgroup=start')
        ],[
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇꜱ', url=UPDATES_LINK),
            InlineKeyboardButton('ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('ᴄʜᴇᴄᴋ ᴀʟʟ ᴄʜᴀɴɴᴇʟꜱ', url='https://t.me/hd_movies_hub01/7')
        ]]
        await query.message.edit_text(text=script.START_TXT.format(query.from_user.mention, get_wish()), reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('ꜱᴛᴀᴛᴜꜱ', callback_data='stats'),
            InlineKeyboardButton('ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ', callback_data='source')
        ],[
            InlineKeyboardButton('ʙᴏᴛ ᴏᴡɴᴇʀ', callback_data='owner')
        ],[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='start')
        ]]
        await query.message.edit_text(text=script.MY_ABOUT_TXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

    elif query.data == "stats":
        if query.from_user.id not in ADMINS:
            return await query.answer("ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)
        files = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        premium = await db.all_premium_users()
        u_size = get_size(await db.get_db_size())
        f_size = get_size(536870912 - await db.get_db_size())
        uptime = get_readable_time(time_now() - temp.START_TIME)
        buttons = [[InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='about')]]
        await query.message.edit_text(script.STATUS_TXT.format(files, users, chats, premium, u_size, f_size, uptime), reply_markup=InlineKeyboardMarkup(buttons))
        
    elif query.data == "owner":
        # Bot Owner button is already static, but the inner text uses the contact name.
        buttons = [[InlineKeyboardButton(text=f"ᴄᴏɴᴛᴀᴄᴛ - {(await client.get_users(admin)).first_name}", user_id=admin)] for admin in ADMINS]
        buttons.append([InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='about')])
        await query.message.edit_text(text=script.MY_OWNER_TXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        
    elif query.data == "earn":
        buttons = [[
            InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ꜱʜᴏʀᴛɴᴇʀ', callback_data='howshort')
        ],[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='start')
        ]]
        await query.message.edit_text(text=script.EARN_TXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        
    elif query.data == "howshort":
        buttons = [[InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='earn')]]
        await query.message.edit_text(text=script.HOW_TXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        
    elif query.data in ["help", "user_command", "admin_command"]:
        buttons = [[
            InlineKeyboardButton('ᴜꜱᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ', callback_data='user_command'),
            InlineKeyboardButton('ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ', callback_data='admin_command')
        ],[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='start')
        ]]
        
        text = script.HELP_TXT
        if query.data == "user_command": text = script.USER_COMMAND_TXT
        elif query.data == "admin_command":
            if query.from_user.id not in ADMINS: return await query.answer("ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)
            text = script.ADMIN_COMMAND_TXT
            
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "source":
        buttons = [[InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='about')]]
        await query.message.edit_text(text=script.SOURCE_TXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
  
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)

        if status == "True":
            await save_group_settings(int(grp_id), set_type, False)
            await query.answer("♻️")
        else:
            await save_group_settings(int(grp_id), set_type, True)
            await query.answer("✅")

        settings = await get_settings(int(grp_id))
        if settings is not None:
            buttons = [
                [InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'), InlineKeyboardButton('✅ ʏᴇꜱ' if settings["auto_filter"] else '♻️ ɴᴏ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')],
                [InlineKeyboardButton('ɪᴍᴅʙ ᴘᴏꜱᴛᴇʀ', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'), InlineKeyboardButton('✅ ʏᴇꜱ' if settings["imdb"] else '♻️ ɴᴏ', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')],
                [InlineKeyboardButton('ꜱᴘᴇʟʟɪɴɢ ᴄʜᴇᴄᴋ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'), InlineKeyboardButton('✅ ʏᴇꜱ' if settings["spell_check"] else '♻️ ɴᴏ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')],
                [InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'), InlineKeyboardButton(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else '♻️ ɴᴏ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')],
                [InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',), InlineKeyboardButton('✅ ʏᴇꜱ' if settings["welcome"] else '♻️ ɴᴏ', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}')],
                [InlineKeyboardButton('ꜱʜᴏʀᴛʟɪɴᴋ', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'), InlineKeyboardButton('✅ ʏᴇꜱ' if settings["shortlink"] else '♻️ ɴᴏ', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}')],
                [InlineKeyboardButton('ʀᴇꜱᴜʟᴛ ᴘᴀɢᴇ', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}'), InlineKeyboardButton('⛓ ʟɪɴᴋ' if settings["links"] else '🧲 ʙᴜᴛᴛᴏɴ', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}')],
                [InlineKeyboardButton('ꜱᴛʀᴇᴀᴍ', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}'), InlineKeyboardButton('✅ ᴏɴ' if settings.get("is_stream", IS_STREAM) else '♻️ ᴏꜰꜰ', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}')],
                [InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close_data')]
            ]
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
        else:
            await query.message.edit_text("ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!")
            
    elif query.data == "delete_all":
        files = await Media.count_documents()
        await query.answer('ᴅᴇʟᴇᴛɪɴɢ...')
        await Media.collection.drop()
        await query.message.edit_text(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {files} ꜰɪʟᴇꜱ")
        
    elif query.data.startswith("delete"):
        _, query_ = query.data.split("_", 1)
        deleted = 0
        await query.message.edit('ᴅᴇʟᴇᴛɪɴɢ...')
        total, files = await delete_files(query_)
        async for file in files:
            await Media.collection.delete_one({'_id': file.file_id})
            deleted += 1
        await query.message.edit(f'ᴅᴇʟᴇᴛᴇᴅ {deleted} ꜰɪʟᴇꜱ ɪɴ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀꜱᴇ ɪɴ ʏᴏᴜʀ ǫᴜᴇʀʏ {query_}')
     
    elif query.data.startswith("send_all"):
        ident, key, req = query.data.split("#")
        if int(req) != query.from_user.id:
            return await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇꜱᴜʟᴛꜱ!", show_alert=True)        
        files = temp.FILES.get(key)
        if not files:
            return await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nꜱᴇɴᴅ ɴᴇᴡ ʀᴇǫᴜᴇꜱᴛ ᴀɢᴀɪɴ!", show_alert=True)        
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}")

    elif query.data == "unmute_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            return await query.answer("ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
        users_id = []
        await query.message.edit("ᴜɴᴍᴜᴛᴇ ᴀʟʟ ꜱᴛᴀʀᴛᴇᴅ! ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ ᴍᴀʏ ᴛᴀᴋᴇ ꜱᴏᴍᴇ ᴛɪᴍᴇ...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id: await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            return await query.message.reply(f'ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code>')
        await query.message.delete()
        if users_id: await query.message.reply(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜɴᴍᴜᴛᴇᴅ <code>{len(users_id)}</code> ᴜꜱᴇʀꜱ.")
        else: await query.message.reply('ɴᴏᴛʜɪɴɢ ᴛᴏ ᴜɴᴍᴜᴛᴇ ᴜꜱᴇʀꜱ.')

    elif query.data == "unban_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            return await query.answer("ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
        users_id = []
        await query.message.edit("ᴜɴʙᴀɴ ᴀʟʟ ꜱᴛᴀʀᴛᴇᴅ! ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ ᴍᴀʏ ᴛᴀᴋᴇ ꜱᴏᴍᴇ ᴛɪᴍᴇ...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.BANNED):
                users_id.append(member.user.id)
            for user_id in users_id: await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            return await query.message.reply(f'ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code>')
        await query.message.delete()
        if users_id: await query.message.reply_text(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜɴʙᴀɴɴᴇᴅ <code>{len(users_id)}</code> ᴜꜱᴇʀꜱ.")
        else: await query.message.reply_text('ɴᴏᴛʜɪɴɢ ᴛᴏ ᴜɴʙᴀɴ ᴜꜱᴇʀꜱ.')

    elif query.data == "kick_muted_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            return await query.answer("ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
        users_id = []
        await query.message.edit("ᴋɪᴄᴋ ᴍᴜᴛᴇᴅ ᴜꜱᴇʀꜱ ꜱᴛᴀʀᴛᴇᴅ! ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ ᴍᴀʏ ᴛᴀᴋᴇ ꜱᴏᴍᴇ ᴛɪᴍᴇ...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id: await client.ban_chat_member(query.message.chat.id, user_id, datetime.now() + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            return await query.message.reply_text(f'ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code>')
        await query.message.delete()
        if users_id: await query.message.reply_text(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴋɪᴄᴋᴇᴅ ᴍᴜᴛᴇᴅ <code>{len(users_id)}</code> ᴜꜱᴇʀꜱ.")
        else: await query.message.reply_text('ɴᴏᴛʜɪɴɢ ᴛᴏ ᴋɪᴄᴋ ᴍᴜᴛᴇᴅ ᴜꜱᴇʀꜱ.')

    elif query.data == "kick_deleted_accounts_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            return await query.answer("ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
        users_id = []
        await query.message.edit("ᴋɪᴄᴋ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ ꜱᴛᴀʀᴛᴇᴅ! ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ ᴍᴀʏ ᴛᴀᴋᴇ ꜱᴏᴍᴇ ᴛɪᴍᴇ...")
        try:
            async for member in client.get_chat_members(query.message.chat.id):
                if member.user.is_deleted: users_id.append(member.user.id)
            for user_id in users_id: await client.ban_chat_member(query.message.chat.id, user_id, datetime.now() + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            return await query.message.reply_text(f'ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code>')
        await query.message.delete()
        if users_id: await query.message.reply_text(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴋɪᴄᴋᴇᴅ ᴅᴇʟᴇᴛᴇᴅ <code>{len(users_id)}</code> ᴀᴄᴄᴏᴜɴᴛꜱ.")
        else: await query.message.reply_text('ɴᴏᴛʜɪɴɢ ᴛᴏ ᴋɪᴄᴋ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ.')

    elif query.data == "buy_premium":
        btn = [[InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=OWNER_USERNAME)],[InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close_data")]]
        await query.message.edit_media(InputMediaPhoto(media=PAYMENT_QR, caption=script.PREMIUM_PLAN_TEXT.format(OWNER_UPI_ID)))
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(btn))

async def advantage_spell_chok(message, s):
    search = message.text
    google_search = search.replace(" ", "+")
    btn = [[
        InlineKeyboardButton("ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ", callback_data='instructions'),
        InlineKeyboardButton("ꜱᴇᴀʀᴄʜ ɢᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={google_search}")
    ],[
        InlineKeyboardButton("ʀᴇǫᴜᴇꜱᴛ ᴛᴏ ʙᴏᴛ ᴀᴅᴍɪɴ", url="https/t.me/mpbotzsupport_bot")
    ]]
    try:
        movies = await get_poster(search, bulk=True)
    except:
        try:
            n = await s.edit_text(text=script.NOT_FILE_TXT.format(message.from_user.mention, search), reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(60)
            await n.delete()
        except: pass
        try: await message.delete()
        except: pass
        return
    if not movies:
        try:
            n = await s.edit_text(text=script.NOT_FILE_TXT.format(message.from_user.mention, search), reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(60)
            await n.delete()
        except: pass
        try: await message.delete()
        except: pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [[InlineKeyboardButton(text=movie.get('title').upper(), callback_data=f"spolling#{movie.movieID}#{user}")] for movie in movies]
    buttons.append([InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close_data")])
    try:
        s = await s.edit_text(text=f"👋 ʜᴇʟʟᴏ {message.from_user.mention},\n\nɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ <b>'{search}'</b> ʏᴏᴜ ʀᴇǫᴜᴇꜱᴛᴇᴅ.\nꜱᴇʟᴇᴄᴛ ɪꜰ ʏᴏᴜ ᴍᴇᴀɴᴛ ᴏɴᴇ ᴏꜰ ᴛʜᴇꜱᴇ? 👇", reply_markup=InlineKeyboardMarkup(buttons))
    except:
        pass
    await asyncio.sleep(300)
    try: await s.delete()
    except: pass
    try: await message.delete()
    except: pass