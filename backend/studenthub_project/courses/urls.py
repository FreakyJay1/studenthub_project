from django.urls import path
from . import views

urlpatterns = [
    path('<str:user_id>/update-courses/', views.scrape_and_recommend_courses_view, name='update_courses'),
    path('<str:user_id>/recommended-courses/', views.get_recommended_courses_view, name='get_recommended_courses')
]