from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('recommend-partners/<str:user_id>/', views.recommend_study_partners_view, name='recommend_study_partners'),
]