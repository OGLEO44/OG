#CREDITS TO @CyberTGX


import asyncio
from pyrogram.errors import FloodWait
from pyrogram import enums
from mfinder import LOGGER
from motor.motor_asyncio import AsyncIOMotorCollection

async def users_info(bot, users_collection: AsyncIOMotorCollection):
    users = 0
    blocked = 0

    cursor = users_collection.find({}, {"_id": 1})
    
    identity = [user['_id'] async for user in cursor] 
    
    for user_id in identity:
        user_id = int(user_id) 
        is_active = False 
        try:
            name = await bot.send_chat_action(user_id, enums.ChatAction.TYPING)
            is_active = bool(name)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            is_active = True 
        except Exception:
            is_active = False
            
        if is_active:
            users += 1
        else:
            result = await users_collection.delete_one({"_id": user_id})
            if result.deleted_count > 0:
                LOGGER.info("Deleted user id %s from broadcast list (MongoDB)", user_id)
                blocked += 1
            else:
                LOGGER.warning("Attempted to delete user id %s, but not found (MongoDB)", user_id)
            
    return users, blocked



