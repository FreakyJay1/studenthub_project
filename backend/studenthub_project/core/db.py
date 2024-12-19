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