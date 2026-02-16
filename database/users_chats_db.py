import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME, SHORTENER_API, SHORTENER_WEBSITE, SPELL_CHECK

client = AsyncIOMotorClient(DATABASE_URI)
mydb = client[DATABASE_NAME]

class Database:
    def __init__(self):
        self.col = mydb.users
        self.grp = mydb.groups
        self.req = mydb.requests # For Auto-Approve logic
        self.botcol = mydb.botcol

    # --- USER LOGIC ---
    async def add_user(self, id, name):
        user = await self.get_user(id)
        if user:
            return
        user_data = {
            "id": id,
            "name": name,
            "expiry_time": None, # Premium Logic
            "points": 0,         # Referral Points
            "is_banned": False,
            "ban_reason": ""
        }
        await self.col.insert_one(user_data)

    async def get_user(self, id):
        return await self.col.find_one({"id": int(id)})

    async def update_user(self, data):
        """Updates premium status, referral points etc"""
        await self.col.update_one({"id": int(data['id'])}, {"$set": data}, upsert=True)

    # --- PREMIUM & EXPIRY (Repo 3 DNA) ---
    async def get_expiry(self, id):
        user = await self.get_user(id)
        return user.get("expiry_time") if user else None

    async def remove_premium(self, id):
        await self.col.update_one({"id": int(id)}, {"$set": {"expiry_time": None}})

    # --- GROUP & SETTINGS LOGIC ---
    async def add_group(self, id, title):
        group = await self.get_group(id)
        if group:
            return
        group_data = {
            "id": id,
            "title": title,
            "chat_type": "group",
            "spell_check": SPELL_CHECK,
            "shortner": SHORTENER_WEBSITE,
            "api": SHORTENER_API
        }
        await self.grp.insert_one(group_data)

    async def get_group(self, id):
        return await self.grp.find_one({"id": int(id)})

    # --- ANALYTICS ---
    async def total_users_count(self):
        return await self.col.count_documents({})

    async def total_groups_count(self):
        return await self.grp.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    # --- BAN LOGIC (Repo 3 Admin Controls) ---
    async def ban_user(self, user_id, reason="No Reason"):
        await self.col.update_one(
            {"id": user_id}, 
            {"$set": {"is_banned": True, "ban_reason": reason}}
        )

db = Database()
