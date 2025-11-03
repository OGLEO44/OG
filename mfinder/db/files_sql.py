#CREDITS TO @CyberTGX

import threading
from mongoengine import connect, Document, StringField, DecimalField, IntField, NotUniqueError, Q
from mfinder import DB_URL, LOGGER
from mfinder.utils.helpers import unpack_new_file_id

try:
    connect(host=DB_URL)
    LOGGER.info("Successfully connected to MongoDB.")
except Exception as e:
    LOGGER.error("Failed to connect to MongoDB: %s", str(e))


class Files(Document):
    """
    Represents a file document in the 'files' collection in MongoDB.
    file_id is set as unique. file_name is set as sparse unique to allow
    multiple documents with a null file_name without index failure.
    """
    file_name = StringField(required=True)
    file_id = StringField(required=True, unique=True) 
    file_ref = StringField()
    file_size = DecimalField() 
    file_type = StringField()
    mime_type = StringField()
    caption = StringField(default=None)

    meta = {
        'collection': 'files', 
        'indexes': [
            {'fields': ['file_name'], 'unique': True, 'sparse': True},
            {'fields': ['file_name', 'caption'], 'name': 'search_index'},
        ]
    }

INSERTION_LOCK = threading.RLock()



async def save_file(media):
    """
    Saves a file document. Checks for existence by file_id OR file_name before saving.
    """
    file_id, file_ref = unpack_new_file_id(media.file_id)
    with INSERTION_LOCK:
        try:
            if Files.objects(file_id=file_id).first():
                LOGGER.warning("%s is already saved in the database (via file_id)", media.file_name)
                return False

            file = Files(
                file_name=media.file_name,
                file_id=file_id,
                file_ref=file_ref,
                file_size=media.file_size,
                file_type=media.file_type,
                mime_type=media.mime_type,
                caption=media.caption if media.caption else None,
            )
            file.save()
            LOGGER.info("%s is saved in database", media.file_name)
            return True

        except NotUniqueError:
            LOGGER.warning("%s is already saved in the database (via unique constraint)", media.file_name)
            return False
        except Exception as e:
            LOGGER.warning(
                "Error occurred while saving file in database: %s", str(e)
            )
            return False


async def get_filter_results(query, page=1, per_page=10):
    """
    Searches for files where file_name or caption contains any of the query words (case-insensitive, partial match).
    """
    try:
        with INSERTION_LOCK:
            offset = (page - 1) * per_page
            search_words = query.split()
            conditions = []
            for word in search_words:
                conditions.append(Q(file_name__iregex=word) | Q(caption__iregex=word))
            
            combined_query = Files.objects.filter(*conditions).order_by('file_name')
            
            total_count = combined_query.count()
            files = combined_query.skip(offset).limit(per_page)
            
            return list(files), total_count
            
    except Exception as e:
        LOGGER.warning("Error occurred while retrieving filter results: %s", str(e))
        return [], 0


async def get_precise_filter_results(query, page=1, per_page=10):
    """
    Searches for files where file_name or caption contains the query words as whole words (case-insensitive).
    """
    try:
        with INSERTION_LOCK:
            offset = (page - 1) * per_page
            search_words = query.split()
            
            conditions = []
            for word in search_words:
                regex_pattern = r'\b' + word + r'\b'
                conditions.append(Q(file_name__iregex=regex_pattern) | Q(caption__iregex=regex_pattern))
            
            combined_query = Files.objects.filter(*conditions).order_by('file_name')
            
            total_count = combined_query.count()
            files = combined_query.skip(offset).limit(per_page)
            
            return list(files), total_count
            
    except Exception as e:
        LOGGER.warning("Error occurred while retrieving filter results: %s", str(e))
        return [], 0


async def get_file_details(file_id):
    """
    Retrieves all files matching the given file_id.
    """
    try:
        with INSERTION_LOCK:
            file_details = Files.objects(file_id=file_id)
            return list(file_details)
    except Exception as e:
        LOGGER.warning("Error occurred while retrieving file details: %s", str(e))
        return []


async def delete_file(media):
    """
    Deletes a file document by file_id.
    """
    file_id, file_ref = unpack_new_file_id(media.file_id)
    try:
        with INSERTION_LOCK:
            file = Files.objects(file_id=file_id).first()
            if file:
                file.delete() 
                return True
            
            LOGGER.warning("File to delete not found: %s", str(file_id))
            return "Not Found"

    except Exception as e:
        LOGGER.warning("Error occurred while deleting file: %s", str(e))
        return False


async def count_files():
    """
    Counts the total number of file documents.
    """
    try:
        with INSERTION_LOCK:
            total_count = Files.objects.count()
            return total_count
    except Exception as e:
        LOGGER.warning("Error occurred while counting files: %s", str(e))
        return 0
