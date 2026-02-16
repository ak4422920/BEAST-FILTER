from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import AUTH_CHANNEL, ADMINS
from database.users_chats_db import db

@Client.on_message(filters.incoming & filters.private, group=-1)
async def forcesub_handler(client, message):
    if message.from_user.id in ADMINS:
        return # Admins are exempt

    # 1. Identify if this is a Clone or Main Bot
    # 
    me = await client.get_me()
    is_clone = False
    fsub_id = AUTH_CHANNEL # Default Main Bot Channel
    
    # Clone check logic from Repo 2
    if me.is_bot and me.username != "YourMainBotUsername": 
        is_clone = True
        clone_data = await db.get_clone_settings(me.id) # Fetch clone owner settings
        if clone_data and clone_data.get("fsub"):
            fsub_id = clone_data["fsub"]

    if not fsub_id:
        return # No FSub set

    try:
        # Check if user is in channel
        await client.get_chat_member(fsub_id, message.from_user.id)
    except UserNotParticipant:
        # 2. User not in channel - Show Join Button
        invite_link = await client.create_chat_invite_link(fsub_id)
        
        btn = [[
            InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite_link.invite_link)
        ],[
            InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=start")
        ]]
        
        await message.reply_text(
            text=f"<b>❌ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ!\n\nʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ. ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴄʟɪᴄᴋ ᴏɴ 'ᴛʀʏ ᴀɢᴀɪɴ' ʙᴜᴛᴛᴏɴ.</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        message.stop_propagation() # Stop other plugins from working
