import re
from os import environ
from Script import script

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# --- 1. CORE BOT SETTINGS ---
SESSION = environ.get("SESSION", "Beast_Filter")
API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]

# --- 2. DATABASE SETTINGS (Repo 1 & 2 Dual-DB Logic) ---
DATABASE_NAME = environ.get("DATABASE_NAME", "BeastDB")
DATABASE_URI = environ.get("DATABASE_URI", "") # Main User DB
FILE_DB_URI = environ.get("FILE_DB_URI", "") # Primary File DB
SEC_FILE_DB_URI = environ.get("SEC_FILE_DB_URI", "") # Secondary File DB for massive scaling
CLONE_DATABASE_URI = environ.get("CLONE_DATABASE_URI", "") # For Public Cloning System
COLLECTION_NAME = environ.get("COLLECTION_NAME", "Beast_Media")

# --- 3. MONETIZATION & VERIFICATION (Repo 3 Jisshu Triple Logic) ---
SHORTENER_WEBSITE = environ.get("SHORTENER_WEBSITE", "")
SHORTENER_API = environ.get("SHORTENER_API", "")
SHORTENER_WEBSITE2 = environ.get("SHORTENER_WEBSITE2", "")
SHORTENER_API2 = environ.get("SHORTENER_API2", "")
SHORTENER_WEBSITE3 = environ.get("SHORTENER_WEBSITE3", "")
SHORTENER_API3 = environ.get("SHORTENER_API3", "")
TWO_VERIFY_GAP = int(environ.get("TWO_VERIFY_GAP", "14400")) # 4 Hours Gap
THREE_VERIFY_GAP = int(environ.get("THREE_VERIFY_GAP", "14400"))
TUTORIAL = environ.get("TUTORIAL", "")
TUTORIAL_2 = environ.get("TUTORIAL_2", "")
TUTORIAL_3 = environ.get("TUTORIAL_3", "")

# --- 4. AI & UTILITY TOOLS (Repo 4 Lucy Suite) ---
IMAGINE_API_KEY = environ.get("IMAGINE_API_KEY", "") # AI Image Gen
RMBG_API_KEY = environ.get("RMBG_API_KEY", "") # Background Remover
TMDB_API_KEY = environ.get("TMDB_API_KEY", "") # Movie Info
APPROVAL_WAIT_TIME = int(environ.get("APPROVAL_WAIT_TIME", "10")) # Delayed Approval

# --- 5. LOGS & CHANNELS ---
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))
AUTH_CHANNEL = int(environ.get("AUTH_CHANNEL", "")) # For ForceSub
AUTH_REQ_CHANNEL = int(environ.get("AUTH_REQ_CHANNEL", "")) # Join Request FSub
DELETE_CHANNELS = [int(ch) for ch in environ.get("DELETE_CHANNELS", "0").split()]

# --- 6. PERFORMANCE & UI ---
WORKERS = int(environ.get("WORKERS", "150")) # Extreme Performance from Repo 2
URL = environ.get("FQDN", "") # For Streaming and Web Player
REACTIONS = ["👀", "😱", "🔥", "😍", "🎉", "🥰", "😇", "⚡"] # Jisshu Style Reactions
MAX_BTN = int(environ.get("MAX_BTN", "8"))
AUTO_DELETE = is_enabled(environ.get("AUTO_DELETE", "True"), True)
DELETE_TIME = int(environ.get("DELETE_TIME", 1200)) # Auto delete results in 20 mins

# --- 7. TOGGLES ---
STREAM_MODE = is_enabled(environ.get("STREAM_MODE", "True"), True)
RENAME_MODE = is_enabled(environ.get("RENAME_MODE", "True"), True)
AUTO_APPROVE_MODE = is_enabled(environ.get("AUTO_APPROVE_MODE", "True"), True)
SPELL_CHECK = is_enabled(environ.get("SPELL_CHECK", "True"), True)
