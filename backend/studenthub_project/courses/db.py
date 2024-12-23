from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
import logging
from core.db import update_user_recommended_courses, get_user
from django.core.cache import cache

logger = logging.getLogger(__name__)

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE_NAME]

# Helper Functions.
# Helper function to convert string ID to ObjectId, handling errors.
def _get_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        logger.warning(f"Invalid ObjectId string: {id_str}")
        return None

# Course Data functions.

# Retrieves courses from database based on the search terms.
def get_courses_from_db(search_terms=None):
    cache_key = f"courses:{':'.join(search_terms)}" if search_terms else "courses:all"
    courses = cache.get(cache_key)
    if courses is None:
        courses_collection = db["courses"]
        try:
            query = {}
            if search_terms:
                query["$or"] = [
                    {"title": {"$regex": term, "$options": "i"}} for term in search_terms
                ]
            courses = list(courses_collection.find(query))
            cache.set(cache_key, courses, timeout=3600)
            logger.info(f"Retrieved courses from database for search_terms: {search_terms}")
        except PyMongoError as e:
            logger.error(f"Error retrieving courses from MongoDB: {e}")
            return []
    else:
        logger.info(f"Retrieved courses from cache for key: {cache_key}")
    return courses

# Stores scraped course data in the database.
def store_courses_data(courses_data):
    if not courses_data:
        return
    courses_collection = db["courses"]
    try:
        courses_collection.delete_many({})
        courses_collection.insert_many(courses_data)
        logger.info(f"Stored {len(courses_data)} courses in MongoDB")
        cache.delete_pattern("courses:*")
    except PyMongoError as e:
        logger.error(f"Error storing courses in MongoDB: {e}")

# Recommends courses to user based on their profile and scraped data.
def recommend_courses_to_user(user_id):
    user = get_user(user_id)
    if not user:
        logger.error(f"User not found: {user_id}")
        return False
    user_interests = user.get("favorite_path", [])
    user_learning_style = user.get("preferred_learning_style", [])
    courses_data = get_courses_from_db()
    if not courses_data:
        logger.error("No course data found for recommendations.")
        return False
    recommended_courses = []
    for course in courses_data:
        if any(interest.lower() in course["title"].lower() for interest in user_interests):
            recommended_courses.append(course)
            continue
        if any(style.lower() in course.get("description", "").lower() for style in user_learning_style):
            recommended_courses.append(course)
    success = update_user_recommended_courses(user_id, recommended_courses)
    return success