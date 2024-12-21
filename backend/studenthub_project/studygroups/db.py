from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from datetime import datetime
from messaging.db import create_group_conversation,add_user_to_group_conversation, create_notification, remove_user_from_group_conversation
from pymongo.errors import PyMongoError
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE_NAME]

# Helper function.

# Helper function to convert string ID to ObjectId, handling errors.
def _get_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        logger.warning(f"Invalid ObjectId string: {id_str}")
        return None
    
# Study Group Functions.

# Creating a new study group in the database.
def create_study_group(name, description, member_ids, creator_id):
    study_groups_collection = db["study_groups"]
    try:
        members = [ObjectId(uid) for uid in member_ids]
        creator_oid = ObjectId(creator_id)
        if creator_oid not in members:
            members.append(creator_oid)
        group_data = {
            "name": name,
            "description": description,
            "members": members,
            "created_by": creator_oid,
            "created_at": datetime.now()
        }
        result = study_groups_collection.insert_one(group_data)
        group_id = str(result.inserted_id)
        create_group_conversation(name, [str(m) for m in members], creator_id)
        return group_id
    except PyMongoError as e:
        logger.error(f"Error creating study group: {e}")
        return None
    
# Retrieves a study group by their ID with caching.
def get_study_group(group_id):
    study_groups_collection = db["study_groups"]
    cache_key = f"study_group:{group_id}"
    group = cache.get(cache_key)
    if group is not None:
        logger.info(f"Cache hit for study group ID: {group_id}")
        return group
    group_oid = _get_object_id(group_id)
    if not group_oid:
        logger.warning(f"Attempted to get study group with invalid ID format: {group_id}")
        return None
    try:
        group = study_groups_collection.find_one({"_id": group_oid})
        if group:
            cache.set(cache_key, group, timeout=300)
            return group
        else:
            logger.info(f"Study group not found with ID: {group_id}")
            return None
    except PyMongoError as e:
        logger.error(f"Error retrieving study group: {e}")
        return None
    
# Adding a user into the study group.
def add_user_to_study_group(group_id, user_id, admin_id):
    study_groups_collection = db["study_groups"]
    group_oid = _get_object_id(group_id)
    user_oid = _get_object_id(user_id)
    admin_oid = _get_object_id(admin_id)
    if not group_oid or not user_oid or not admin_oid:
        logger.warning(f"Attempted to add user to study group with invalid ID format: group_id={group_id}, user_id={user_id}")
        return False
    try:
        group = study_groups_collection.find_one({"_id": group_oid})
        if group is None or group["created_by"] != admin_oid:
            logger.warning(f"User {admin_id} is not authorized to add users to group {group_id}")
            return False
        result = study_groups_collection.update_one(
            {"_id": group_oid},
            {"$addToSet": {"members": user_oid}}
        )
        if result.modified_count > 0:
            cache.delete(f"study_group:{group_id}")
            success = add_user_to_group_conversation(group_id,user_id, admin_id)
            if not success:
                raise Exception("Failed to add user to the group chat.")
            group = get_study_group(group_id)
            if group:
                group_name = group["name"]
                notification_data = {
                    "recipient_id": user_oid,
                    "message": f"You have been added to the study group '{group_name}'",
                    "is_read": False,
                    "timestamp": datetime.now()
                }
            create_notification(notification_data)
            return True
        else:
            logger.info(f"User {user_id} was already a member of group {group_id} or group not found")
            return False
    except PyMongoError as e:
        logger.error(f"Error adding user to the study group: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False

# Retrieves all study groups that a user is a part of.
def get_study_groups_for_user(user_id):
    study_groups_collection = db["study_groups"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        logger.warning(f"Attempted to get study groups for user with invaild ID format: {user_id}")
        return []
    try:
        cache_key = f"study_groups_for_user:{user_id}"
        cached_groups = cache.get(cache_key)
        if cached_groups is not None:
            logger.info(f"Cache hit for study groups for user ID: {user_id}")
            return cached_groups
        groups = list(study_groups_collection.find({"members": user_oid}))
        cache.set(cache_key, groups, timeout=300)
        return groups
    except PyMongoError as e:
        logger.error(f"Error retrieving study groups for user: {e}")
        return []
    
# Removes a user from that study group.
def remove_user_from_study_group(group_id, user_id, admin_id):
    study_groups_collection = db["study_groups"]
    group_oid = _get_object_id(group_id)
    user_oid = _get_object_id(user_id)
    admin_oid = _get_object_id(admin_id)
    if not group_oid or not user_oid or not admin_oid:
        logger.warning(f"Attempted to remove user from study group with invalid ID format: group_id={group_id}, user_id={user_id}")
        return False
    try:
        group = study_groups_collection.find_one({"_id": group_oid})
        if group is None or group["created_by"] != admin_oid:
            logger.warning(f"User {admin_id} is not authorized to remove users from group {group_id}")
            return False
        result = study_groups_collection.update_one(
            {"_id": group_oid},
            {"$pull": {"members": user_oid}}   
        )
        cache.delete(f"study_group:{group_id}")
        if result.modified_count > 0:
            success = remove_user_from_group_conversation(group_id, user_id, admin_id)
            if not success:
                logger.error(f"Failed to remove user {user_id} from group chat for study group {group_id}")
            else:
                logger.info(f"User {user_id} removed from group chat for study group {group_id}")
            return True
        else:
            logger.info(f"User {user_id} was not a member of group {group_id} or group not found")
            return False
    except PyMongoError as e:
        logger.error(f"Error removing user from study group: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False

# Delete the study group by their ID.
def delete_study_group(group_id):
    study_groups_collection = db["study_groups"]
    group_oid = _get_object_id(group_id)
    if not group_oid:
        logger.warning(f"Attempted to delete study group with invalid ID format: {group_id}")
        return False
    try:
        result = study_groups_collection.delete_one({"_id": group_oid})
        cache.delete(f"study_group:{group_id}")
        if result.deleted_count > 0:
            return True
        else:
            logger.info(f"Study group not found with ID: {group_id}")
            return False
    except PyMongoError as e:
        logger.error(f"Error deleting study group: {e}")
        return False