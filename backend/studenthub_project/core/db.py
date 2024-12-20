from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError, DuplicateKeyError
import logging

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

# To retrieves a user info from mongodb database by their ID.
def get_user(user_id):
    user_collection = db["users"]
    user_oid = _get_object_id(user_id)
    if not user_oid:
        return None
    try:
        return user_collection.find_one({"_id": user_oid})
    except PyMongoError as e:
        logger.error(f"Error retrieving user by ID: {e}")
        return None

# To retrieves a user info from mongodb database by thier email.
def get_user_by_email(email):
    user_collection = db["users"]
    try:
        return user_collection.find_one({"email": email})
    except PyMongoError as e:
        logger.error(f"Error retrieving user by email: {e}")
        return None
    
# Retrieves potential study partners for user base on multiple criteria.
def get_potential_study_partners(user_id, limit=10):
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
        return potential_partners[:limit]
    except PyMongoError as e:
        logger.error(f"Error in get_potential_study_partners: {e}")
        return []
    