#CREDITS TO @CyberTGX
import threading
from pymongo import MongoClient
from mfinder import DB_URL  

DB_NAME = "mfinder_db"

CLIENT = None
DB = None
COLLECTION = None

def start_mongo():
    """Initializes the MongoDB client and collection."""
    global CLIENT, DB, COLLECTION
    try:
        CLIENT = MongoClient(DB_URL)
        DB = CLIENT[DB_NAME]
        COLLECTION = DB["banlist"]
        print("MongoDB connection established.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

start_mongo()

INSERTION_LOCK = threading.RLock()


async def ban_user(user_id: int) -> bool:
    """
    Adds a user ID to the ban list collection. Returns True if the user was added or was already present.
    """
    with INSERTION_LOCK:
        try:
            if COLLECTION.find_one({"user_id": user_id}):
                return True  
            
            COLLECTION.insert_one({"user_id": user_id})
            return True
        except Exception as e:
            print(f"Error in ban_user: {e}")
            return False


async def is_banned(user_id: int) -> int | bool:
    """
    Checks if a user is banned. Returns the user_id (int) if banned, otherwise False.
    """
    with INSERTION_LOCK:
        try:
            usr = COLLECTION.find_one({"user_id": user_id})
            
            return usr["user_id"] if usr else False
        except Exception as e:
            print(f"Error in is_banned: {e}")
            return False


async def unban_user(user_id: int) -> bool:
    """
    Removes a user ID from the ban list. Returns True if the user was removed, False if not found.
    """
    with INSERTION_LOCK:
        try:
            result = COLLECTION.delete_one({"user_id": user_id})
            
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error in unban_user: {e}")
            return False
