from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import PyMongoError
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE_NAME]

# Helper Functions

# Helper function to convert string ID to ObjectId and Handling errors.
def _get_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        return None

# Functions for messagin user to user.

# Creating a new message in database
def create_message(sender_id,receiver_id, content):
    messages_collection = db["messages"]
    try:
        message = {
            "sender_id": ObjectId(sender_id),
            "receiver_id": ObjectId(receiver_id),
            "content": content,
            "timestamp": datetime.now(),
            "read": False
        }
        result = messages_collection.insert_one(message)
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"Error creating message: {e}")
        return None

# Retrieves messages between two user in the database with caching.
def get_messages_between_users(user_id1, user_id2):
    messages_collection = db["messages"]
    user_oid1 = ObjectId(user_id1)
    user_oid2 = ObjectId(user_id2)
    if not user_oid1 or not user_oid2:
        logger.warning(f"Invalid user ID format: user_id1={user_id1}, user_id2={user_id2}")
        return []
    cache_key = f"messages_between:{user_id1}:{user_id2}"
    messages = cache.get(cache_key)
    if messages is None:
        try:
            messages = list(messages_collection.find({
                "$or": [
                    {"sender_id": user_oid1, "receiver_id": user_oid2},
                    {"sender_id": user_oid2, "receiver_id": user_oid1}
                ]
            }).sort("timestamp", 1))
            return messages
        except PyMongoError as e:
            logger.error(f"Error retrieving messages: {e}")
            return []
    else:
        logger.info(f"Retrieved messages from cache for key: {cache_key}")
    return messages

# Retrieves all messages sent or received by a specific user in the database with caching.
def get_all_messages_for_user(user_id):
    messages_collection = db["messages"]
    user_oid = ObjectId(user_id)
    if not user_oid:
        logger.warning(f"Invalid user ID format: {user_id}")
        return []
    cache_key = f"messages_for_user:{user_id}"
    messages = cache.get(cache_key)
    if messages is None:
        try:
            return list(messages_collection.find({
                "$or": [
                    {"sender_id": user_oid},
                    {"receiver_id": user_oid}
                ]
            }).sort("timestamp", 1))
        except PyMongoError as e:
            logger.error(f"Error retrieving messages for user: {e}")
            return []
    else:
        logger.info(f"Retrieved messages from cache for key: {cache_key}")
    return messages
    
# Retrieves all unread messages for specific user in the database.
def get_unread_messges(user_id):
    messages_collection = db["messages"]
    user_oid = ObjectId(user_id)
    if not user_oid:
        logger.warning(f"Invalid user ID format: {user_id}")
        return []
    try:
        return list(messages_collection.find({
            "receiver_id": user_oid,
            "read": False
        }).sort("timestamp", 1))
    except PyMongoError as e:
        logger.error(f"Error retrieving unread messages: {e}")
        return []

# Marks the specific message as read.
def mark_message_as_read(message_id):
    messages_collection = db["messages"]
    message_oid = _get_object_id(message_id)
    if not message_oid:
        logger.warning(f"Invalid message ID format: {message_id}")
        return False
    try:
        result = messages_collection.update_one(
            {"_id": message_oid},
            {"$set": {"read": True}}
        )
        message = messages_collection.find_one({"_id": message_oid})
        if message:
            cache.delete(f"message_between: {message['sender_id']}:{message['receiver_id']}")
            cache.delete(f"messages_between:{message['receiver_id']}:{message['sender_id']}")
            cache.delete(f"messages_for_user:{message['sender_id']}")
            cache.delete(f"messages_for_user:{message['receiver_id']}")
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error marking message as read: {e}")
        return False

# Marks all messages for the user as read.
def mark_all_messages_as_read(user_id):
    messages_collection = db["messages"]
    user_oid = ObjectId(user_id)
    if not user_oid:
        logger.warning(f"Invalid user ID format: {user_id}")
        return 0
    try:
        result = messages_collection.update_many(
            {"receiver_id": user_oid, "read": False},
            {"$set": {"read": True}}
        )
        return result.modified_count
    except PyMongoError as e:
        logger.error(f"Error marking all messages as read: {e}")
        return 0

# Group Conversation Functions.

# Creating a new group conversation in database.
def create_group_conversation(group_name, member_ids, created_by):
    conversations_collection = db["group_conversations"]
    try:
        group_members = [ObjectId(member_id) for member_id in member_ids]
    except Exception as e:
        logger.error(f"Error converting member_ids to ObjectIds: {e}")
        return None

    conversation = {
        "group_name": group_name,
        "members": group_members,
        "created_by": ObjectId(created_by),
        "created_at": datetime.now()
    }
    try:
        result = conversations_collection.insert_one(conversation)
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"Error creating group conversation: {e}")
        return None
    
# Adding a new message to the group conversation.
def add_message_to_group_conversation(group_id, sender_id, content):
    messages_collection = db["group_messages"]
    try:
        message = {
            "group_id": ObjectId(group_id),
            "sender_id": ObjectId(sender_id),
            "content": content,
            "timestamp": datetime.now(),
            "read_by": []
        }
        result = messages_collection.insert_one(message)
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"Error adding message to group: {e}")
        return None

# Retrieves all messages for that specific group conversation.
def get_messages_for_group_conversation(group_id):
    messages_collection = db["group_messages"]
    group_oid = ObjectId(group_id)
    if not group_oid:
        logger.warning(f"Invalid group ID format: {group_id}")
        return []
    try:
        return list(messages_collection.find({"group_id": group_oid}).sort("timestamp", 1))
    except PyMongoError as e:
        logger.error(f"Error getting group messages: {e}")
        return []

# Retrieves a group conversation by It's ID in the database with caching.
def get_group_conversation(group_id):
    cache_key = f"group_conversation:{group_id}"
    group_conversation = cache.get(cache_key)
    if group_conversation is None:
        conversations_collection = db["group_conversations"]
        group_oid = _get_object_id(group_id)
        if not group_oid:
            logger.warning(f"Invalid group ID format: {group_id}")
            return None
        try:
            group_conversation = conversations_collection.find_one({"_id": group_oid})
            if group_conversation:
                    cache.set(cache_key, group_conversation, timeout=120)
        except PyMongoError as e:
            logger.error(f"Error retrieving group conversation: {e}")
            return None
    else:
        logger.info(f"Retrieved group conversation from cache for key: {cache_key}")
    return group_conversation

# Adding a user to an existing group conversation, requires admin_id of the creator.
def add_user_to_group_conversation(group_id,user_id, admin_id):
    conversations_collection = db["group_conversations"]
    group_oid = _get_object_id(group_id)
    user_oid = _get_object_id(user_id)
    admin_oid = _get_object_id(admin_id)
    if not group_oid or not user_oid or not admin_oid:
        logger.warning(f"Invalid group ID or user ID format: group_id={group_id}, user_id={user_id}, admin_id= {admin_id}")
        return False
    try:
        group = conversations_collection.find_one({"_id": group_oid, "created_by": admin_oid})
        if not group:
            logger.warning(f"User {admin_id} is not authorized to add users to group {group_id}")
            return False
        result = conversations_collection.update_one(
            {"_id": group_oid},
            {"$addToSet": {"members": user_oid}}
        )
        if result.modified_count > 0:
            cache.delete(f"group_conversation:{group_id}")
            return True
        else:
            logger.info(f"User {user_id} was already a member of group {group_id} or group not found")
            return False
    except PyMongoError as e:
        logger.error(f"Error adding user to group: {e}")
        return False

# Removes a user from that group conversation, requires admin_id of the creator.
def remove_user_from_group_conversation(group_id, user_id, admin_id):
    conversations_collection = db["group_conversations"]
    group_oid = _get_object_id(group_id)
    user_oid = _get_object_id(user_id)
    admin_oid = _get_object_id(admin_id)
    if not group_oid or not user_oid or not admin_oid:
        logger.warning(f"Invalid group ID or user ID format: group_id={group_id}, user_id={user_id}, admin_id={admin_id}")
        return False
    try:
        group = conversations_collection.find_one({"_id": group_oid, "created_by": admin_oid})
        if not group:
            logger.warning(f"User {admin_id} is not authorized to remove users from group {group_id}")
            return False
        result = conversations_collection.update_one(
            {"_id": group_oid},
            {"$pull": {"members": user_oid}}
        )
        if result.modified_count > 0:
            cache.delete(f"group_conversation:{group_id}")
            return True
        else:
            logger.info(f"User {user_id} was not a member of group {group_id} or group not found")
            return False
    except PyMongoError as e:
        logger.error(f"Error removing user from group: {e}")
        return False

# Retrieves all group conversation that a user is apart of.
def get_group_conversations_for_user(user_id):
    conversations_collection = db["group_conversations"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        logger.warning(f"Invalid user ID format: {user_id}")
        return []
    try:
        return list(conversations_collection.find({"members": user_oid}))
    except PyMongoError as e:
        logger.error(f"Error retrieving group conversations for user: {e}")
        return []

# Marks a specfic group message as read by the user.
def mark_group_message_as_read(group_message_id, user_id):
    messages_collection = db["group_messages"]
    message_oid = _get_object_id(group_message_id)
    user_oid = _get_object_id(user_id)
    if not message_oid or not user_oid:
        logger.warning(f"Invalid message ID or user ID format: group_message_id={group_message_id}, user_id={user_id}")
        return False
    try:
        result = messages_collection.update_one(
            {"_id": message_oid},
            {"$addToSet": {"read_by": user_oid}}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error marking group message as read: {e}")
        return False

# deletes a group conversation and all its messages.
def delete_group_conversation(group_id):
    conversations_collection = db["group_conversations"]
    messages_collection = db["group_messages"]
    group_oid = _get_object_id(group_id)
    if not group_oid:
        logger.warning(f"Invalid group ID format: {group_id}")
        return False
    try:
        delete_convo_result = conversations_collection.delete_one({"_id": group_oid})
        delete_messages_result = messages_collection.delete_many({"group_id": group_oid})
        cache.delete(f"group_conversation:{group_id}")
        if delete_convo_result.deleted_count > 0:
            logger.info(f"Group conversation {group_id} and its messages deleted successfully.")
            return True
        else:
            logger.warning(f"Group conversation {group_id} not found or no messages deleted.")
            return False
    except PyMongoError as e:
        logger.error(f"Error deleting group conversation: {e}")
        return False

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False

# Notification Functions

# Creating a new notification in the database.
def create_notification(notification_data):
    notifications_collection = db["notifications"]
    try:
        result = notifications_collection.insert_one(notification_data)
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"Error creating notification: {e}")
        return None

# Retrieves notifications for the user.
def get_notifications_for_user(user_id, read=None):
    notifications_collection = db["notifications"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        logger.warning(f"Invalid user ID format: {user_id}")
        return []
    query = {"recipient_id": ObjectId(user_id)}
    if read is not None:
        query["is_read"] = read
    try:
        return list(notifications_collection.find(query).sort("timestamp", -1))
    except PyMongoError as e:
        logger.error(f"Error retrieving notifications: {e}")
        return []

# Marks a notification as read.
def mark_notification_as_read(notification_id):
    notifications_collection = db["notifications"]
    notification_oid = _get_object_id(notification_id)
    if not notification_oid:
        logger.warning(f"Invalid notification ID format: {notification_id}")
        return False
    try:
        result = notifications_collection.update_one(
            {"_id": notification_oid},
            {"$set": {"is_read": True}}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error marking notification as read: {e}")
        return False

# Functions to search messages by keyword.

# Searches messages sent or received by a user for a query string.
def search_messages_for_user(user_id, query_string):
    messages_collection = db["messages"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        logger.warning(f"Invalid user ID format: {user_id}")
        return []
    try:
        messages = list(messages_collection.find({
            "$or": [
                {"sender_id": user_oid},
                {"receiver_id": user_oid}
            ],
            "$text": {"$search": query_string}
        }).sort("timestamp", 1))
        return messages
    except PyMongoError as e:
        logger.error(f"Error searching messages for user: {e}")
        return []

# Searches group messages for a user for a query string.
def search_group_messages_for_user(user_id, query_string):
    messages_collection = db["group_messages"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        logger.warning(f"Invalid user ID format: {user_id}")
        return []
    try:
        group_conversations = db["group_conversations"].find({"members": user_oid}, {"_id": 1})
        group_ids = [conversation["_id"] for conversation in group_conversations]
        messages = list(messages_collection.find({
            "group_id": {"$in": group_ids},
            "$text": {"$search": query_string}
        }).sort("timestamp", 1))
        return messages
    except PyMongoError as e:
        logger.error(f"Error searching group messages for user: {e}")
        return []