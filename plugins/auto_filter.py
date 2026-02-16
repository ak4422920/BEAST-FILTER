import re
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import *
from database.ia_filterdb import get_search_results
from database.users_chats_db import db
from fuzzywuzzy import process # Repo 2 AI suggestion logic
from Script import script

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.text.startswith("/"):
        return # Ignore commands

    query = message.text
    search_msg = await message.reply_text("<b>sᴇᴀʀᴄʜɪɴɢ...</b>")
    
    # 1. Search Database
    files, total = await get_search_results(query, max_results=MAX_BTN)
    
    if not files:
        # 2. AI Spelling Suggestion (Repo 2 Logic)
        await search_msg.delete()
        return await suggest_spelling(client, message, query)

    # 3. Premium & Verification Check (Repo 3 Logic)
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    # Check if user is premium
    is_premium = False
    if user and user.get("expiry_time"):
        if user["expiry_time"] > datetime.datetime.now():
            is_premium = True

    # 4. Generate Buttons
    btn = []
    for file in files:
        btn.append([InlineKeyboardButton(
            text=f"[{humanbytes(file.file_size)}] {file.file_name}",
            callback_data=f"files#{file.file_id}"
        )])

    if not is_premium:
        btn.insert(0, [InlineKeyboardButton("⭐ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ (ɴᴏ ᴀᴅs) ⭐", callback_data="buy_premium")])

    await search_msg.edit(
        text=f"<b>ʜᴇʀᴇ ɪ ғᴏᴜɴᴅ ʀᴇsᴜʟᴛs ғᴏʀ: {query}\nᴛᴏᴛᴀʟ ʀᴇsᴜʟᴛs: {total}</b>",
        reply_markup=InlineKeyboardMarkup(btn)
    )

async def suggest_spelling(client, message, query):
    # This simulates Repo 2's fuzzy search suggestion
    # We would fetch all movie names and find the closest match
    # For now, we provide the UI hook:
    await message.reply_text(
        text=script.SPELL_CHECK_TXT.format(query),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 sᴇᴀʀᴄʜ ᴀɢᴀɪɴ", switch_inline_query_current_chat=query)]
        ])
    )
