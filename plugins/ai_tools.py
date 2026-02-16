import os
import time
import requests
import aiohttp
import aiofiles
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from lexica import AsyncClient # For Upscaling
from info import IMAGINE_API_KEY, RMBG_API_KEY
from Script import script

# --- 1. AI Image Generation (/imagine) ---
@Client.on_message(filters.command(['imagine', 'generate']))
async def imagine_ai(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘʀᴏᴍᴘᴛ! ᴇx:</b> `/imagine a futuristic tiger`")
    
    prompt = " ".join(message.command[1:])
    wait_msg = await message.reply_text("<b>ʙᴇᴀsᴛ ᴀɪ ɪs ᴅʀᴀᴡɪɴɢ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ 🎨</b>")
    start_time = time.time()

    url = 'https://ai-api.magicstudio.com/api/ai-art-generator'
    form_data = {
        'prompt': prompt,
        'output_format': 'bytes',
        'user_is_subscribed': 'false',
    }

    try:
        response = requests.post(url, data=form_data)
        if response.status_code == 200:
            photo_path = "beast_ai.jpg"
            with open(photo_path, 'wb') as f:
                f.write(response.content)
            
            await wait_msg.delete()
            await message.reply_photo(
                photo=photo_path,
                caption=f"<b>✨ ɢᴇɴᴇʀᴀᴛᴇᴅ ʙʏ ʙᴇᴀsᴛ ᴀɪ\n⏱️ ᴛɪᴍᴇ ᴛᴀᴋᴇɴ: {round(time.time()-start_time, 2)}s\n🔍 ᴘʀᴏᴍᴘᴛ: {prompt}</b>"
            )
            os.remove(photo_path)
        else:
            await wait_msg.edit_text("<b>ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ɪᴍᴀɢᴇ. ᴀᴘɪ ɪssᴜᴇ!</b>")
    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴇʀʀᴏʀ: {str(e)}</b>")

# --- 2. Photo Upscaling (/upscale) ---
@Client.on_message(filters.command("upscale"))
async def upscale_image(client, message):
    if not (message.reply_to_message and message.reply_to_message.photo):
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ ᴜᴘsᴄᴀʟᴇ ɪᴛ!</b>")
    
    wait_msg = await message.reply_text("<b>ᴜᴘsᴄᴀʟɪɴɢ ǫᴜᴀʟɪᴛʏ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ 🚀</b>")
    file_path = await client.download_media(message.reply_to_message.photo.file_id)
    
    lexica_client = AsyncClient() #
    try:
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        
        upscaled_bytes = await lexica_client.upscale(image_bytes)
        upscaled_path = "upscaled_beast.png"
        
        with open(upscaled_path, "wb") as f:
            f.write(upscaled_bytes)
        
        await message.reply_photo(upscaled_path, caption="<b>🔥 ǫᴜᴀʟɪᴛʏ ᴜᴘsᴄᴀʟᴇᴅ ʙʏ ʙᴇᴀsᴛ ᴀɪ!</b>")
        os.remove(upscaled_path)
    except Exception as e:
        await wait_msg.edit_text(f"<b>ᴜᴘsᴄᴀʟᴇ ᴇʀʀᴏʀ: {str(e)}</b>")
    finally:
        await lexica_client.close()
        os.remove(file_path)
        await wait_msg.delete()

# --- 3. Background Remover (/rmbg) ---
@Client.on_message(filters.command("rmbg"))
async def remove_background(client, message):
    if not (message.reply_to_message and message.reply_to_message.photo):
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ ʀᴇᴍᴏᴠᴇ ʙᴀᴄᴋɢʀᴏᴜɴᴅ!</b>")
    
    wait_msg = await message.reply_text("<b>ᴇʀᴀsɪɴɢ ʙᴀᴄᴋɢʀᴏᴜɴᴅ... ⏳</b>")
    photo = await client.download_media(message.reply_to_message)
    
    headers = {"X-API-Key": RMBG_API_KEY} #
    files = {"image_file": open(photo, "rb").read()}
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.remove.bg/v1.0/removebg", headers=headers, data=files) as resp:
            if resp.status_code == 200:
                output_path = "no_bg.png"
                async with aiofiles.open(output_path, "wb") as f:
                    await f.write(await resp.read())
                
                await message.reply_document(output_path, caption="<b>✅ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ʀᴇᴍᴏᴠᴇᴅ!</b>")
                os.remove(output_path)
            else:
                await wait_msg.edit_text("<b>ᴇʀʀᴏʀ: ᴄʜᴇᴄᴋ ɪꜰ ʏᴏᴜʀ ʀᴍʙɢ ᴀᴘɪ ᴋᴇʏ ɪs ᴠᴀʟɪᴅ.</b>")
    
    os.remove(photo)
    await wait_msg.delete()
