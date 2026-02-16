import logging
import logging.config
from pyrogram import Client, idle
from info import *
from Jisshu.bot.clients import initialize_clients # Repo 3 Scaling
from Jisshu.util.keepalive import ping_server      # Stability
from database.ia_filterdb import Media            # Repo 2/3 Search Index
from aiohttp import web
from plugins import web_server                     # Streaming Server
import asyncio

# Logging Setup
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class BeastBot(Client):
    def __init__(self):
        super().__init__(
            name="BeastFilter",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=WORKERS, # Using 150 Workers for extreme speed
            plugins={"root": "plugins"}, # Merged plugins folder
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        logger.info(f"⚡ {me.first_name} (BEAST FILTER) is now Online!")

        # 1. Multi-Client Initialization (Repo 3 Logic)
        # Yeh bot ko multiple sub-bots ke saath connect karega taaki limit na aaye.
        await initialize_clients()

        # 2. Database Indexing (Repo 3)
        # Search ko fast banane ke liye media indexes ko refresh karega.
        await Media.ensure_indexes()

        # 3. Start Streaming Web Server (Repo 1 & 2)
        # Isse user movies ko bina download kiye online dekh payenge.
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        logger.info(f"🌐 Web Server started on port {PORT}")

        # 4. Background Tasks
        # Bot ko "Sleep Mode" mein jane se rokne ke liye ping karega.
        asyncio.create_task(ping_server())

    async def stop(self, *args):
        await super().stop()
        logger.info("❌ BEAST FILTER is shutting down...")

if __name__ == "__main__":
    # Event loop start
    loop = asyncio.get_event_loop()
    bot = BeastBot()
    
    try:
        loop.run_until_complete(bot.start())
        idle() # Bot ko running state mein rakhega
    except KeyboardInterrupt:
        loop.run_until_complete(bot.stop())
    finally:
        loop.close()
