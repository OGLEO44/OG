#CREDITS TO @CyberTGX

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from mfinder import DB_URL  
import threading


MONGO_CLIENT = AsyncIOMotorClient(DB_URL)
DB_NAME = 'mfinder_db'  
DB = MONGO_CLIENT[DB_NAME]
BROADCAST_COLLECTION = DB['broadcast'] 

INSERTION_LOCK = threading.RLock()


async def add_user(user_id: int, user_name: str):
    """Adds a new user or updates the name if the user_id exists."""
    with INSERTION_LOCK:
        await BROADCAST_COLLECTION.update_one(
            {'user_id': user_id},
            {'$set': {'user_id': user_id, 'user_name': user_name}},
            upsert=True
        )


async def is_user(user_id: int) -> bool:
    """Checks if a user exists by user_id."""
    with INSERTION_LOCK:
        user_doc = await BROADCAST_COLLECTION.find_one(
            {'user_id': user_id}, 
            {'_id': 0, 'user_id': 1} 
        )
        return bool(user_doc)


async def query_msg() -> list[int]:
    """Queries all user_ids, ordered by user_id."""
    cursor = BROADCAST_COLLECTION.find(
        {}, 
        {'_id': 0, 'user_id': 1} 
    ).sort('user_id', 1) 
    
    user_ids = []
    async for doc in cursor:
        user_ids.append(doc['user_id'])
        
    return user_ids


async def del_user(user_id: int):
    """Deletes a user by user_id."""
    with INSERTION_LOCK:
        await BROADCAST_COLLECTION.delete_one(
            {'user_id': user_id}
        )
