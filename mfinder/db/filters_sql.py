#CREDITS TO @CyberTGX

import threading
from pymongo import MongoClient
from mfinder import DB_URL, DB_NAME  
CLIENT = None
DB = None
COLLECTION = None

def start_mongo():
    """Initializes the MongoDB client and collection."""
    global CLIENT, DB, COLLECTION
    try:
        CLIENT = MongoClient(DB_URL)
        DB = CLIENT[DB_NAME]
        COLLECTION = DB["filters"]
        print("MongoDB connection established.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

start_mongo()

INSERTION_LOCK = threading.RLock()

async def add_filter(filters: str, message: str) -> bool:
    """
    Adds a new filter or updates the message of an existing one.
    Case-insensitive check for 'filters' field.
    """
    with INSERTION_LOCK:
        try:
            result = COLLECTION.update_one(
                {"filters": {"$regex": f"^{filters}$", "$options": "i"}},
                {"$set": {"filters": filters, "message": message}},
                upsert=True
            )
            return result.matched_count > 0 or result.upserted_id is not None

        except Exception as e:
            print(f"Error in add_filter: {e}")
            return False


async def is_filter(filters: str) -> dict | bool:
    """
    Checks if a filter exists and returns the document if found.
    Case-insensitive check for 'filters' field.
    """
    with INSERTION_LOCK:
        try:
            fltr = COLLECTION.find_one(
                {"filters": {"$regex": f"^{filters}$", "$options": "i"}}
            )
            return fltr if fltr else False
        except Exception as e:
            print(f"Error in is_filter: {e}")
            return False


async def rem_filter(filters: str) -> bool:
    """
    Removes a filter from the collection.
    Case-insensitive check for 'filters' field.
    """
    with INSERTION_LOCK:
        try:
            result = COLLECTION.delete_one(
                {"filters": {"$regex": f"^{filters}$", "$options": "i"}}
            )
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error in rem_filter: {e}")
            return False


async def list_filters() -> list[str] | bool:
    """
    Returns a list of all filter names.
    """
    try:
        fltrs = COLLECTION.find({}, {"filters": 1, "_id": 0})
        return [fltr["filters"] for fltr in fltrs]
    except Exception as e:
        print(f"Error in list_filters: {e}")
        return False
