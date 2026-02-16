import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import FILE_DB_URI, DATABASE_NAME, COLLECTION_NAME

# Initialize MongoDB Client with Dual-DB Support logic
client = AsyncIOMotorClient(FILE_DB_URI)
mydb = client[DATABASE_NAME]
instance = Instance.from_db(mydb)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute=\"_id\")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)
    file_type = fields.StrField(allow_none=True)

    class Meta:
        indexes = (\"$file_name\",) # Fast text search indexing
        collection_name = COLLECTION_NAME

async def save_file(media):
    \"\"\"Saves a file to the database and avoids duplicates\"\"\"
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r\"(_|\\-|\\.|\\+)\", \" \", str(media.file_name))
    
    try:
        media_doc = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            mime_type=media.mime_type,
            caption=media.caption if media.caption else \"\",
            file_type=media.file_type
        )
        await media_doc.commit()
        return \"saved\"
    except DuplicateKeyError:
        return \"exists\"

async def get_search_results(query, file_type=None, max_results=10):
    \"\"\"The Core Search Logic - Beast Mode\"\"\"
    query = query.strip()
    if not query:
        return [], 0
        
    # Regex for flexible movie name matching
    raw_pattern = query.replace(\" \", r\".*[\\s\\.\\+\\-_]\")
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return [], 0

    filter_query = {\"file_name\": regex}
    if file_type:
        filter_query[\"file_type\"] = file_type

    total_results = await Media.count_documents(filter_query)
    cursor = Media.find(filter_query)
    
    # Sort by natural order (most recent first)
    cursor.sort(\"$natural\", -1)
    
    files = await cursor.to_list(length=max_results)
    return files, total_results

# --- Helper Functions for File ID Processing ---
def unpack_new_file_id(new_file_id):
    \"\"\"Decodes the file ID for database storage\"\"\"
    decoded = FileId.decode(new_file_id)
    file_id = base64.urlsafe_b64encode(pack(\"<ii\", decoded.dc_id, decoded.id)).decode().rstrip(\"=\")
    return file_id, decoded.file_reference
