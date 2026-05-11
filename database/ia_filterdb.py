import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN

client = AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME

async def save_file(media):
    file_id = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(file_id=file_id, file_name=file_name, file_size=media.file_size)
    except ValidationError:
        return 'err'
    else:
        try:
            await file.commit()
        except DuplicateKeyError:      
            return 'dup'
        else:
            return 'suc'

async def get_search_results(query, max_results=MAX_BTN, offset=0, locks=None):
    query = str(query).strip()
    locks = locks or {}
    
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]') 
        
    try: regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except: regex = query

    filter_query = {'file_name': regex}
    
    # HARD LOCK SYSTEM -> Applied seamlessly
    and_conditions = []
    if locks.get('lang'): and_conditions.append({'file_name': re.compile(f"(?i){locks['lang']}")})
    if locks.get('qual'): and_conditions.append({'file_name': re.compile(f"(?i){locks['qual']}")})
    if locks.get('season'): and_conditions.append({'file_name': re.compile(f"(?i)(s|season\s?){locks['season']}\b")})
    if locks.get('episode'): and_conditions.append({'file_name': re.compile(f"(?i)(e|ep|episode\s?){locks['episode']}\b")})
    if locks.get('year'): and_conditions.append({'file_name': re.compile(f"(?i){locks['year']}")})

    if and_conditions:
        filter_query = {'$and': [filter_query] + and_conditions}

    cursor = Media.find(filter_query)
    cursor.sort('$natural', -1)
    
    cursor.skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)
    total_results = await Media.count_documents(filter_query)
    
    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = ''       
    return files, next_offset, total_results

async def get_dynamic_filters(query, locks, filter_type):
    # Quick scan of active pool to determine what options exist for UI
    files, _, _ = await get_search_results(query, locks=locks, max_results=500) 
    available = set()
    
    from info import LANGUAGES, QUALITY
    
    for file in files:
        fname = file.file_name.lower()
        if filter_type == 'lang':
            for item in LANGUAGES:
                if item in fname: available.add(item)
        elif filter_type == 'qual':
            for item in QUALITY:
                if item in fname: available.add(item)
        elif filter_type == 'year':
            years = re.findall(r'\b(19\d{2}|20\d{2})\b', fname)
            for y in years: available.add(y)
        elif filter_type == 'season':
            seasons = re.findall(r'\b(?:s|season\s?)(\d{1,2})\b', fname)
            for s in seasons: available.add(str(int(s)))
        elif filter_type == 'episode':
            eps = re.findall(r'\b(?:e|ep|episode\s?)(\d{1,2})\b', fname)
            for e in eps: available.add(str(int(e)))
            
    if filter_type in ['year', 'season', 'episode']:
        return sorted(list(available), key=lambda x: int(x))
    return list(available)
    
async def delete_files(query):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try: regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except: regex = query
    filter = {'file_name': regex}
    total = await Media.count_documents(filter)
    files = Media.find(filter)
    return total, files

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0: n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack("<iiqq", int(decoded.file_type), decoded.dc_id, decoded.media_id, decoded.access_hash)
    )
    return file_id