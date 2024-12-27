from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from datetime import datetime
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE_NAME]

# Helper Functions

# Helper function to convert string ID to ObjectId, handling errors.
def _get_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        logger.warning(f"Invalid ObjectId string: {id_str}")
        return None

# Resources Functions.

# Creates a new resource document in database (admin only).
def create_resource(resource_data, admin_user_id):
    resources_collection = db["resources"]
    resource_data["created_by"] = ObjectId(admin_user_id)
    resource_data["created_at"] = datetime.now()
    resource_data["updated_at"] = datetime.now()
    try:
        result = resources_collection.insert_one(resource_data)
        resource_id = str(result.inserted_id)
        cache.delete("resources:all")
        return resource_id
    except PyMongoError as e:
        logger.error(f"Error creating resource: {e}")
        return None

# Retrieves a resource from database by ID, with caching.
def get_resource(resource_id):
    cache_key = f"resource:{resource_id}"
    resource = cache.get(cache_key)
    if resource is None:
        resources_collection = db["resources"]
        resource_oid = _get_object_id(resource_id)
        if not resource_oid:
            logger.warning(f"Invalid resource ID format: {resource_id}")
            return None
        try:
            resource = resources_collection.find_one({"_id": resource_oid})
            if resource:
                cache.set(cache_key, resource, timeout=300)  # Cache for 5 minutes
                logger.info(f"Fetched resource {resource_id} from database")
            else:
                logger.info(f"Resource not found with ID: {resource_id}")
                return None
        except PyMongoError as e:
            logger.error(f"Error retrieving resource by ID: {e}")
            return None
    else:
        logger.info(f"Retrieved resource {resource_id} from cache")
    return resource

# Updates a resource in database (Admin only).
def update_resource(resource_id, resource_data, admin_user_id):
    resources_collection = db["resources"]
    resource_oid = _get_object_id(resource_id)
    if not resource_oid:
        logger.warning(f"Invalid resource ID format: {resource_id}")
        return False
    try:
        resource_data["updated_at"] = datetime.now()
        result = resources_collection.update_one(
            {"_id": resource_oid},
            {"$set": resource_data}
        )
        if result.modified_count > 0:
            cache.delete(f"resource:{resource_id}")
            cache.delete("resources:all")
            logger.info(f"Updated resource {resource_id} in database")
            return True
        else:
            logger.info(f"Resource not found with ID: {resource_id} for update")
            return False
    except PyMongoError as e:
        logger.error(f"Error updating resource: {e}")
        return False
    
# Deletes a resource from database (Admin only).
def delete_resource(resource_id, admin_user_id):
    resources_collection = db["resources"]
    resource_oid = _get_object_id(resource_id)
    if not resource_oid:
        logger.warning(f"Invalid resource ID format: {resource_id}")
        return False
    try:
        result = resources_collection.delete_one({"_id": resource_oid})
        if result.deleted_count > 0:
            cache.delete(f"resource:{resource_id}")
            cache.delete("resources:all")
            logger.info(f"Deleted resource {resource_id} from database")
            return True
        else:
            logger.info(f"Resource not found with ID: {resource_id}")
            return False
    except PyMongoError as e:
        logger.error(f"Error deleting resource: {e}")
        return False

# Retrieves all resources from database, with caching.
def get_all_resources():
    cache_key = "resources:all"
    resources = cache.get(cache_key)
    if resources is None:
        resources_collection = db["resources"]
        try:
            resources = list(resources_collection.find())
            cache.set(cache_key, resources, timeout=300)  # Cache for 5 minutes
            logger.info("Fetched all resources from database")
        except PyMongoError as e:
            logger.error(f"Error retrieving all resources: {e}")
            return []
    else:
        logger.info("Retrieved all resources from cache")
    return resources

# Searches resources based on a query string, with caching.
def search_resources(query):
    cache_key = f"resources_search:{query}"
    resources = cache.get(cache_key)
    if resources is None:
        resources_collection = db["resources"]
        try:
            resources = list(resources_collection.find({"$text": {"$search": query}}))
            cache.set(cache_key, resources, timeout=300)
            logger.info(f"Performed text search for resources with query: '{query}'")
        except PyMongoError as e:
            logger.error(f"Error searching resources: {e}")
            return []
    else:
        logger.info(f"Retrieved search results from cache for query: '{query}'")
    return resources
