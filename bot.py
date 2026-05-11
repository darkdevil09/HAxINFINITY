import time, os, asyncio
import logging
from logging.handlers import RotatingFileHandler
from pyrogram import Client
from database.ia_filterdb import Media
from aiohttp import web
from database.users_chats_db import db
from web import web_app
from info import LOG_CHANNEL, API_ID, API_HASH, BOT_TOKEN, PORT, BIN_CHANNEL, ADMINS, DATABASE_URL, SUPPORT_GROUP
from utils import temp, get_readable_time, save_group_settings
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from pyrogram.errors import FloodWait
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# --- ADVANCED LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("bot_logs.txt", maxBytes=5000000, backupCount=10),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)
# ------------------------------

class Bot(Client):
    def __init__(self):
        super().__init__(
            name='Auto_Filter_Bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"},
            workers=2000,
            sleep_threshold=20
        )

    async def start(self):
        temp.START_TIME = time.time()
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        
        client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))
        try:
            client.admin.command('ping')
            logger.info("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            logger.error(f"Something Went Wrong While Connecting To Database! {e}", exc_info=True)
            exit()
            
        await super().start()
        
        if os.path.exists('restart.txt'):
            with open("restart.txt") as file:
                chat_id, msg_id = map(int, file)
            try:
                await self.edit_message_text(chat_id=chat_id, message_id=msg_id, text='ʀᴇꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ! ✅')
            except Exception as e:
                logger.warning(f"Failed to edit restart message: {e}")
            os.remove('restart.txt')
            
        temp.BOT = self
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        temp.U_LINK = me.mention
        
        logger.info(f"{me.first_name} ɪꜱ ꜱᴛᴀʀᴛᴇᴅ ɴᴏᴡ 🤗")
        
        app = web.AppRunner(web_app)
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        logger.info(f"Web server started on port {PORT}")
        
        try:
            await self.send_message(chat_id=LOG_CHANNEL, text=f"<b>{me.mention} ʀᴇꜱᴛᴀʀᴛᴇᴅ! 🤖</b>")
        except Exception as e:
            logger.error(f"Error - Make sure bot is admin in LOG_CHANNEL: {e}")
            exit()
            
        try:
            m = await self.send_message(chat_id=BIN_CHANNEL, text="ᴛᴇꜱᴛ")
            await m.delete()
        except Exception as e:
            logger.error(f"Error - Make sure bot is admin in BIN_CHANNEL: {e}")
            exit()
            
        try:
            for admin in ADMINS:
                await self.send_message(chat_id=admin, text=f"<b>✅ ʙᴏᴛ ʀᴇꜱᴛᴀʀᴛᴇᴅ</b>")
            await self.send_message(chat_id=SUPPORT_GROUP, text=f"{me.mention} ʀᴇꜱᴛᴀʀᴛᴇᴅ ✅")
        except Exception as e:
            logger.warning(f"Unable to send message in support group/admins: {e}")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot Stopped! Bye...")

    async def iter_messages(self: Client, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1

app = Bot()

try:
    logger.info("Starting Bot...")
    app.run()
except FloodWait as mp:
    # BUG FIXED: Using wait_time_str to avoid shadowing 'time' module
    wait_time_str = get_readable_time(mp.value)
    logger.warning(f"ꜰʟᴏᴏᴅ ᴡᴀɪᴛ ᴏᴄᴄᴜʀʀᴇᴅ, ꜱʟᴇᴇᴘɪɴɢ ꜰᴏʀ {wait_time_str}")
    
    # BUG FIXED: time.sleep() instead of asyncio.sleep() outside of async loop
    time.sleep(mp.value) 
    
    logger.info("ɴᴏᴡ ʀᴇᴀᴅʏ ꜰᴏʀ ᴅᴇᴘʟᴏʏɪɴɢ !")
    app.run()
except Exception as e:
    logger.critical("Fatal error occurred in main loop!", exc_info=True)