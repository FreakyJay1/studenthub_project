from celery import shared_task
from .db import get_courses_from_db, store_courses_data, recommend_courses_to_user
from core.db import get_user, update_user_recommended_courses
from .scraper import scrape_course_data
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Scrapes course data, stores it in the database, and updates user recommendations.
@shared_task
def scrape_courses_and_recommend(user_id, search_terms):
    try:
        user = get_user(user_id)
        if not user:
            logger.error(f"User not found for ID: {user_id} in scrape_courses_and_recommend")
            return
        base_url = settings.SCRAPE_CONFIG.get('base_url')
        courses_data = scrape_course_data(base_url, search_terms)
        if courses_data:
            store_courses_data(courses_data)
        else:
            logger.warning(f"Failed to scrape course data for search terms: {search_terms}")
            return
        courses_data = get_courses_from_db(search_terms)
        if not courses_data:
            logger.error("No course data found for recommendations.")
            return
        recommended_courses = []
        user_interests = user.get("favorite_path", [])
        user_learning_style = user.get("preferred_learning_style", [])
        for course in courses_data:
            if any(interest.lower() in course["title"].lower() for interest in user_interests):
                recommended_courses.append(course)
                continue
            if any(style.lower() in course.get("description", "").lower() for style in user_learning_style):
                recommended_courses.append(course)
        if recommended_courses:
            success = update_user_recommended_courses(user_id, recommended_courses)
            if success:
                logger.info(f"Recommended courses updated for user ID: {user_id}")
            else:
                logger.error(f"Failed to update recommended courses for user ID: {user_id}")
        else:
            logger.info(f"No courses matched for user ID: {user_id} based on the criteria")
    except Exception as e:
        logger.error(f"An error occurred in scrape_courses_and_recommend for user ID: {user_id}: {e}")