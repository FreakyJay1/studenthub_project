from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from datetime import datetime
from messaging.db import create_group_conversation,add_user_to_group_conversation, create_notification
from pymongo.errors import PyMongoError
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
def create_study_group(name, description, member_ids):
    study_groups_collection = db["study_groups"]
    try:
        members = [ObjectId(uid) for uid in member_ids]
        group_data = {
            "name": name,
            "description": description,
            "members": members,
            "created_at": datetime.now()
        }
        result = study_groups_collection.insert_one(group_data)
        group_id = str(result.inserted_id)
        create_group_conversation(name, member_ids)
        return group_id
    except PyMongoError as e:
        logger.error(f"Error creating study group: {e}")
        return None
    
# Retrieves a study group by their ID.
def get_study_group(group_id):
    study_groups_collection = db["study_groups"]
    group_oid = _get_object_id(group_id)
    if not group_oid:
        logger.warning(f"Attempted to get study group with invalid ID format: {group_id}")
        return None
    try:
        group = study_groups_collection.find_one({"_id": group_oid})
        if group:
            return group
        else:
            logger.info(f"Study group not found with ID: {group_id}")
            return None
    except PyMongoError as e:
        logger.error(f"Error retrieving study group: {e}")
        return None
    
# Adding a user into the study group.
def add_user_to_study_group(group_id, user_id):
    study_groups_collection = db["study_groups"]
    group_oid = _get_object_id(group_id)
    user_oid = _get_object_id(user_id)
    if not group_oid or not user_oid:
        logger.warning(f"Attempted to add user to study group with invalid ID format: group_id={group_id}, user_id={user_id}")
        return False
    try:
        result = study_groups_collection.update_one(
            {"_id": group_oid},
            {"$addToSet": {"members": user_oid}}
        )
        if result.modified_count > 0:
            success = add_user_to_group_conversation(group_id,user_id)
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

# Retrieves all study groups that a user is a part of.
def get_study_groups_for_user(user_id):
    study_groups_collection = db["study_groups"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        logger.warning(f"Attempted to get study groups for user with invaild ID format: {user_id}")
        return []
    try:
        return list(study_groups_collection.find({"members": user_oid}))
    except PyMongoError as e:
        logger.error(f"Error retrieving study groups for user: {e}")
        return []

# Removes a user from that study group.
def remove_user_from_study_group(group_id, user_id):
    study_groups_collection = db["study_groups"]
    group_oid = _get_object_id(group_id)
    user_oid = _get_object_id(user_id)
    if not group_oid or not user_oid:
        logger.warning(f"Attempted to remove user from study group with invalid ID format: group_id={group_id}, user_id={user_id}")
        return False
    try:
        result = study_groups_collection.update_one(
            {"_id": group_oid},
            {"$pull": {"members": user_oid}}   
        )
        if result.modified_count > 0:
            return True
        else:
            logger.info(f"User {user_id} was not a member of group {group_id} or group not found")
            return False
    except PyMongoError as e:
        logger.error(f"Error removing user from study group: {e}")
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
        return result.deleted_count > 0
    except PyMongoError as e:
        logger.error(f"Error deleting study group: {e}")
        return False