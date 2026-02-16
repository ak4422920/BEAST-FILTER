import os
import requests
import aiohttp
from io import BytesIO
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from info import LOG_CHANNEL

# --- 1. PERMANENT TORRENT SCRAPER (No API Key Required) ---
@Client.on_message(filters.command("torrent"))
async def torrent_search(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɴᴀᴍᴇ! ᴇx:</b> `/torrent deadpool`")
    
    query = " ".join(message.command[1:])
    wait_msg = await message.reply_text("<b>sᴇᴀʀᴄʜɪɴɢ ɪɴ ᴛʜᴇ ᴅᴇᴇᴘ ᴡᴇʙ... 📡</b>")
    
    # 1337x Mirror URL (Always working)
    base_url = "https://1337xx.to" 
    search_url = f"{base_url}/search/{query}/1/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Step 1: Scrape Search Results
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.select('table.table-list tbody tr')
        
        if not results:
            return await wait_msg.edit_text("<b>❌ ɴᴏ ᴛᴏʀʀᴇɴᴛs ғᴏᴜɴᴅ! ᴛʀʏ ᴀɴᴏᴛʜᴇʀ ɴᴀᴍᴇ.</b>")

        # Get Top Result Details
        first_result = results[0]
        name = first_result.select('td.name a')[1].text
        torrent_link = base_url + first_result.select('td.name a')[1]['href']
        seeds = first_result.select_one('td.seeds').text
        size_full = first_result.select_one('td.size').text
        size = size_full.split('B')[0] + 'B'

        # Step 2: Get Magnet Link from Detail Page
        detail_res = requests.get(torrent_link, headers=headers, timeout=10)
        detail_soup = BeautifulSoup(detail_res.content, 'html.parser')
        magnet_link = detail_soup.select_one('a[href^="magnet:"]')['href']

        res_text = f"<b>📂 ғɪʟᴇ ɴᴀᴍᴇ:</b> <code>{name}</code>\n\n" \
                   f"<b>🔖 sɪᴢᴇ:</b> <code>{size}</code>\n" \
                   f"<b>👥 sᴇᴇᴅᴇʀs:</b> <code>{seeds}</code>\n\n" \
                   f"<b>📡 ᴍᴀɢɴᴇᴛ ʟɪɴᴋ:</b>\n<code>{magnet_link}</code>"

        await wait_msg.edit_text(res_text)

    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴇʀʀᴏʀ:</b> <code>ᴡᴇʙsɪᴛᴇ ɪs ᴅᴏᴡɴ ᴏʀ ʙʟᴏᴄᴋᴇᴅ!</code>")

# --- 2. PINTEREST SCRAPER (/image) ---
@Client.on_message(filters.command(["image", "img"]))
async def pinterest_scraper(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>ɢɪᴠᴇ ᴀ ɴᴀᴍᴇ ᴛᴏ sᴇᴀʀᴄʜ ɪᴍᴀɢᴇs!</b>")
    
    query = message.text.split(None, 1)[1]
    wait_msg = await message.reply_text("<b>sᴄʀᴀᴘɪɴɢ ɪᴍᴀɢᴇs... 📸</b>")
    
    try:
        images = requests.get(f"https://pinterest-api-one.vercel.app/?q={query}").json()
        media_group = []
        for url in images["images"][:6]: # Limit to 6 images
            media_group.append(InputMediaPhoto(media=url))
        
        await client.send_media_group(chat_id=message.chat.id, media=media_group, reply_to_message_id=message.id)
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴇʀʀᴏʀ: {e}</b>")

# --- 3. CARBON: CODE TO IMAGE (/carbon) ---
@Client.on_message(filters.command("carbon"))
async def make_carbon_image(client, message):
    replied = message.reply_to_message
    if not (replied and (replied.text or replied.caption)):
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴛᴇxᴛ ᴛᴏ ᴍᴀᴋᴇ ᴄᴀʀʙᴏɴ!</b>")
    
    wait_msg = await message.reply_text("<b>ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴀʀʙᴏɴ... 💻</b>")
    code = replied.text or replied.caption
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://carbonara.solopov.dev/api/cook", json={"code": code}) as resp:
            if resp.status == 200:
                image = BytesIO(await resp.read())
                image.name = "beast_carbon.png"
                await message.reply_photo(image, caption="<b>🔥 ɢᴇɴᴇʀᴀᴛᴇᴅ ʙʏ ʙᴇᴀsᴛ ᴀɪ</b>")
                await wait_msg.delete()
            else:
                await wait_msg.edit_text("<b>ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀʙᴏɴ ɪᴍᴀɢᴇ!</b>")

# --- 4. CLOUD UPLOAD (/cup) ---
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
    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴇʀʀᴏʀ: {e}</b>")
    finally:
        if os.path.exists(path):
            os.remove(path)
