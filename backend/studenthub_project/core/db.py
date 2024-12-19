from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE_NAME]

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
        
    user_data.pop("_id", None)
    
    try:
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Error inserting user into Database: {e}")
        raise

# To retrieves a user info from mongodb database by their ID.
def get_user(user_id):
    user_collection = db["users"]
    
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return None
    
    return user_collection.find_one({"_id": ObjectId(user_id)})

# To retrieves a user info from mongodb database by thier email.
def get_user_email(email):
    user_collection = db["users"]
    return user_collection.find_one({"email": email})