import requests
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from info import LOG_CHANNEL
import aiohttp
from io import BytesIO

# --- 1. Torrent Search (/torrent) - Repo 4 DNA ---
@Client.on_message(filters.command("torrent"))
async def torrent_search(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ! ᴇx:</b> `/torrent deadpool`")
    
    query = " ".join(message.command[1:]).replace(" ", "")
    wait_msg = await message.reply_text("<b>sᴇᴀʀᴄʜɪɴɢ ᴛᴏʀʀᴇɴᴛs... 📡</b>")
    
    try:
        response = requests.get(f"https://api.safone.dev/torrent?query={query}&limit=1")
        if response.status_code == 200:
            data = response.json()['results'][0]
            res = f"<b>📂 ғɪʟᴇ ɴᴀᴍᴇ:</b> <code>{data['name']}</code>\n" \
                  f"<b>🔖 sɪᴢᴇ:</b> <code>{data['size']}</code>\n" \
                  f"<b>📡 ᴍᴀɢɴᴇᴛ ʟɪɴᴋ:</b> <code>{data['magnetLink']}</code>"
            await wait_msg.edit_text(res)
        else:
            await wait_msg.edit_text("<b>ɴᴏ ᴛᴏʀʀᴇɴᴛs ғᴏᴜɴᴅ!</b>")
    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴇʀʀᴏʀ: {e}</b>")

# --- 2. Pinterest Scraper (/image) - Repo 4 DNA ---
@Client.on_message(filters.command(["image", "img"]))
async def pinterest_scraper(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>ɢɪᴠᴇ ᴀ ɴᴀᴍᴇ ᴛᴏ sᴇᴀʀᴄʜ ɪᴍᴀɢᴇs!</b>")
    
    query = message.text.split(None, 1)[1]
    wait_msg = await message.reply_text("<b>sᴄʀᴀᴘɪɴɢ ɪᴍᴀɢᴇs... 📸</b>")
    
    try:
        images = requests.get(f"https://pinterest-api-one.vercel.app/?q={query}").json()
        media_group = []
        for url in images["images"][:6]: # Top 6 images
            media_group.append(InputMediaPhoto(media=url))
        
        await client.send_media_group(chat_id=message.chat.id, media=media_group, reply_to_message_id=message.id)
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴇʀʀᴏʀ: {e}</b>")

# --- 3. Carbon: Code to Image (/carbon) - Repo 4 DNA ---
@Client.on_message(filters.command("carbon"))
async def make_carbon_image(client, message):
    replied = message.reply_to_message
    if not (replied and (replied.text or replied.caption)):
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴛᴇxᴛ ᴛᴏ ᴍᴀᴋᴇ ᴄᴀʀʙᴏɴ!</b>")
    
    wait_msg = await message.reply_text("<b>ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴀʀʙᴏɴ... 💻</b>")
    code = replied.text or replied.caption
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://carbonara.solopov.dev/api/cook", json={"code": code}) as resp:
            image = BytesIO(await resp.read())
            image.name = "beast_carbon.png"
            await message.reply_photo(image, caption="<b>🔥 ɢᴇɴᴇʀᴀᴛᴇᴅ ʙʏ ʙᴇᴀsᴛ ᴀɪ</b>")
            await wait_msg.delete()

# --- 4. Cloud Upload (/cup) - Repo 3 DNA ---
@Client.on_message(filters.command(["cup", "telegraph"]) & filters.reply)
async def cloud_upload(client, message):
    if not message.reply_to_message.media:
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ғɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴛᴏ ᴄʟᴏᴜᴅ!</b>")
    
    wait_msg = await message.reply_text("<b>ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ᴄʟᴏᴜᴅ... ☁️</b>")
    path = await message.reply_to_message.download()
    
    try:
        with open(path, "rb") as f:
            resp = requests.post("https://envs.sh", files={"file": f.read()})
            if resp.status_code == 200:
                await wait_msg.edit_text(f"<b>✅ ᴜᴘʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n<code>{resp.text}</code>")
            else:
                await wait_msg.edit_text("<b>ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ!</b>")
    finally:
        import os
        os.remove(path)
