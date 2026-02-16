import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import *
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_shortlink # Shortener utility

@Client.on_callback_query(filters.regex(r'^files'))
async def handle_file_call(client, query):
    data = query.data.split("#")
    file_id = data[1]
    user_id = query.from_user.id
    
    # 1. Fetch User Data
    user = await db.get_user(user_id)
    
    # 2. Check Premium Status (Repo 3 Logic)
    is_premium = False
    if user and user.get("expiry_time"):
        if user["expiry_time"] > datetime.datetime.now():
            is_premium = True

    if is_premium:
        # Direct File Delivery for VIPs
        return await send_file(client, query, file_id)

    # 3. Verification Logic (Triple Shortener - Repo 3 DNA)
    # Check if user needs to verify (14 hours gap logic)
    verify_status = await db.get_verify_status(user_id)
    
    if not verify_status['is_verified']:
        # Generate Shortener Link
        file_details = await Media.get(file_id)
        # 3-Step Logic: Verification 1, 2, or 3 based on settings
        short_link = await get_shortlink(f"https://t.me/{client.username}?start=file_{file_id}", SHORTENER_WEBSITE, SHORTENER_API)
        
        btn = [
            [InlineKeyboardButton("🔗 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴠᴇʀɪғʏ (ᴀᴅs)", url=short_link)],
            [InlineKeyboardButton("🤔 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ", url=TUTORIAL)]
        ]
        
        return await query.message.edit(
            text=f"<b>⚠️ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ!</b>\n\nʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇ. ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪs ᴠᴀʟɪᴅ ғᴏʀ {TWO_VERIFY_GAP // 3600} ʜᴏᴜʀs.",
            reply_markup=InlineKeyboardMarkup(btn)
        )

    # 4. If Verified, Send File
    await send_file(client, query, file_id)

async def send_file(client, query, file_id):
    file = await client.get_messages(LOG_CHANNEL, int(file_id)) # Logic from Repo 2
    
    # 5. Stream Buttons (Repo 1 & 3 DNA)
    stream_url = f"{URL}watch/{file_id}"
    download_url = f"{URL}download/{file_id}"
    
    btn = [[
        InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ", url=stream_url),
        InlineKeyboardButton("📥 ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download_url)
    ]]
    
    await client.send_cached_media(
        chat_id=query.from_user.id,
        file_id=file.document.file_id,
        caption=ALL_FILES_CAPTION.format(file_name=file.document.file_name, file_size=file.document.file_size),
        reply_markup=InlineKeyboardMarkup(btn)
    )
    await query.answer("ғɪʟᴇ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ ᴘᴍ!")
