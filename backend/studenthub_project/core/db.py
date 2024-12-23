from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from django.conf import settings
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError, DuplicateKeyError
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE_NAME]

# Database Indexes.
# Adds missing indexes to MongoDB collections.
def create_indexes():
    # Indexes for user collection.
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("favorite_path", ASCENDING)])
    db.users.create_index([("preferred_learning_style", ASCENDING)])
    db.users.create_index([("study_preference", ASCENDING)])
    
    # Indexes for messages collection.
    db.messages.create_index([("sender_id", ASCENDING)])
    db.messages.create_index([("receiver_id", ASCENDING)])
    db.messages.create_index([("timestamp", DESCENDING)])
    db.messages.create_index([("content", TEXT)])
    
    # Indexes for group_conversations collection.
    db.group_conversations.create_index([("members", ASCENDING)])
    db.group_conversations.create_index([("group_name", ASCENDING)])
    
    # Indexes for group_messages collection.
    db.group_messages.create_index([("group_id", ASCENDING)])
    db.group_messages.create_index([("sender_id", ASCENDING)])
    db.group_messages.create_index([("timestamp", DESCENDING)])
    db.group_messages.create_index([("content", TEXT)])
    
    # Indexes for notifications collection.
    db.notifications.create_index([("recipient_id", ASCENDING)])
    db.notifications.create_index([("is_read", ASCENDING)])
    db.notifications.create_index([("timestamp", DESCENDING)])
    
    # Indexes for study groups collection.
    db.study_groups.create_index([("members", ASCENDING)])
    db.study_groups.create_index([("name", ASCENDING)])

    logger.info("MongoDB indexes created or verified.")

# Run create_indexes at startup to make sure indexes exist.
create_indexes()

# Helper Functions
# Helper function to convert string ID to ObjectId, handling errors.
def _get_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        logger.warning(f"Invalid ObjectId string: {id_str}")
        return None

# To create user in mongodb database.
def create_user(user_data):
    users_collection = db["users"]
    required_fields = [
        "username", "email", "first_name", "last_name",
        "favorite_programming_languages", "favorite_path", "preferred_learning_style",
        "study_preference", "important_features", "most_used_tool"
    ]
    
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            logger.error(f"Missing required field during user creation: {field}")
            raise ValueError(f"Missing required field: {field}")
    
    if hasattr(user_data["important_features"], "split"):
        user_data["important_features"] = user_data["important_features"].split(",")
    
    user_data.pop("_id", None)
    
    try:
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    except DuplicateKeyError as e:
        logger.error(f"Error creating user: Duplicate key error - {e}")
        raise ValueError("A user with that email already exists.") from e
    except PyMongoError as e:
        logger.error(f"Error inserting user into Database: {e}")
        raise

# To retrieves a user info from mongodb database by their ID with caching.
def get_user(user_id):
    user_collection = db["users"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        return None
    cache_key = f"user:{user_id}"
    user = cache.get(cache_key)
    if user is None:
        try:
            user = user_collection.find_one({"_id": user_oid})
            if user:
                logger.info(f"Fetched user {user_id} from database")
                cache.set(cache_key, user, timeout=300)
            else:
                logger.info(f"User not found with ID: {user_id}")
                return None
        except PyMongoError as e:
            logger.error(f"Error retrieving user by ID: {e}")
            return None
        return user
    else:
        logger.info(f"Retrieved user {user_id} from cache")
    return user

# To retrieves a user info from mongodb database by thier email with caching.
def get_user_by_email(email):
    user_collection = db["users"]
    cache_key = f"user_email:{email}"
    user = cache.get(cache_key)
    if user is None:
        try:
            user = user_collection.find_one({"email": email})
            if user:
                logger.info(f"Fetched user by email {email} from database")
                cache.set(cache_key, user, timeout=300)
            else:
                logger.info(f"User not found with email: {email}")
                return None
        except PyMongoError as e:
            logger.error(f"Error retrieving user by email: {e}")
            return None
        return user
    else:
        logger.info(f"Retrieved user by email {email} from cache")
    return user
    
# Retrieves potential study partners with caching.
def get_potential_study_partners(user_id, limit=10):
    cache_key = f"study_partners:{user_id}:{limit}"
    partners = cache.get(cache_key)
    if partners is None:
        logger.info(f"Fetching study partners for user {user_id} from database")
        users_collection = db["users"]
        user_oid = _get_object_id(user_id)
        if not user_oid:
            logger.warning(f"Invalid user ID format in get_potential_study_partners: {user_id}")
            return []
        current_user = users_collection.find_one({"_id": user_oid})
        if not current_user:
            logger.info(f"User not found with ID: {user_id}")
            return []
        criteria = {
            "_id": {"$ne": user_oid},
            "$or": [
                {"favorite_path": {"$in": current_user.get("favorite_path", [])}},
                {"preferred_learning_style": {"$in": current_user.get("preferred_learning_style", [])}},
                {"study_preference": current_user.get("study_preference")},
                ]
            }
        try:
            potential_partners = list(users_collection.find(criteria))
            for partner in potential_partners:
                score = 0
                if partner.get("favorite_path") == current_user.get("favorite_path"):
                    score += 3
                if partner.get("preferred_learning_style") == current_user.get("preferred_learning_style"):
                    score += 1
                if partner.get("study_preference") == current_user.get("study_preference"):
                    score += 1
                partner["compatibility_score"] = score
            potential_partners.sort(key=lambda x: x.get("compatibility_score", 0), reverse=True)
            partners =  potential_partners[:limit]
            cache.set(cache_key, partners, timeout=180)
        except PyMongoError as e:
            logger.error(f"Error in get_potential_study_partners: {e}")
            return []
    else:
        logger.info(f"Retrieved study partners for user {user_id} from cache")
    return partners

# Updates the recommended courses for a user.
def update_user_recommended_courses(user_id, course_data):
    users_collection = db["users"]
    try:
        user_oid = ObjectId(user_id)
        users_collection.update_one(
            {"_id": user_oid},
            {"$set": {"recommended_courses": course_data}}
        )
        cache.delete(f"user:{user_id}")
        logger.info(f"Updated recommended courses for user {user_id} and invalidated cache")
        return True
    except PyMongoError as e:
        logger.error(f"Error updating recommended courses for user {user_id}: {e}")
        return False