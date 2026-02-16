import logging
from pyrogram import Client, filters
from pyrogram.errors import TokenInvalid, AccessTokenInvalid
from info import API_ID, API_HASH, CLONE_DATABASE_URI
from database.users_chats_db import db # Clone tracking ke liye
import asyncio

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("clone") & filters.private)
async def clone_bot(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>⚠️ ᴜsᴀɢᴇ:</b>\n<code>/clone BOT_TOKEN</code>\n\n"
            "ɢᴇᴛ ʏᴏᴜʀ ᴛᴏᴋᴇɴ ғʀᴏᴍ @BotFather"
        )

    user_id = message.from_user.id
    bot_token = message.command[1]
    wait_msg = await message.reply_text("<b>⏳ ᴠᴇʀɪғʏɪɴɢ ᴛᴏᴋᴇɴ...</b>")

    try:
        # Create a temporary client to check if token is valid
        temp_client = Client(
            name=f"clone_{user_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins={"root": "plugins"} # Same plugins as main bot
        )
        
        await temp_client.start()
        bot_info = await temp_client.get_me()
        
        # Save to Clone Database
        # 
        await db.add_clone(user_id, bot_token)
        
        await wait_msg.edit_text(
            f"<b>✅ ᴄʟᴏɴᴇ sᴜᴄᴄᴇssғᴜʟ!\n\n"
            f"🤖 ʙᴏᴛ ɴᴀᴍᴇ: @{bot_info.username}\n"
            f"👤 ᴏᴡɴᴇʀ: {message.from_user.mention}\n\n"
            f"ʏᴏᴜʀ ʙᴏᴛ ɪs ɴᴏᴡ ʀᴜɴɴɪɴɢ ᴡɪᴛʜ ʙᴇᴀsᴛ ᴍᴏᴅᴇ ꜰᴇᴀᴛᴜʀᴇs!</b>"
        )
        
    except TokenInvalid:
        await wait_msg.edit_text("<b>❌ ɪɴᴠᴀʟɪᴅ ʙᴏᴛ ᴛᴏᴋᴇɴ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ.</b>")
    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴇʀʀᴏʀ:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("clones") & filters.user(ADMINS))
async def list_clones(client, message):
    clones = await db.get_all_clones()
    if not clones:
        return await message.reply_text("<b>ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄʟᴏɴᴇs ʏᴇᴛ!</b>")
    
    msg = "<b>📊 ᴛᴏᴛᴀʟ ᴀᴄᴛɪᴠᴇ ᴄʟᴏɴᴇs:</b>\n\n"
    for count, clone in enumerate(clones, 1):
        msg += f"{count}. <code>{clone['user_id']}</code>\n"
    
    await message.reply_text(msg)
