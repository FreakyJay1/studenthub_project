from django.urls import path
from . import views

urlpatterns = [
    path('studygroups/', views.create_study_group_view, name='create_study_group'),
    path('studygroups/<str:group_id>/', views.get_study_group_view, name='get_study_group'),
    path('studygroups/<str:group_id>/add/', views.add_user_to_study_group_view, name='add_user_to_study_group'),
    path('studygroups/user/<str:user_id>/', views.get_study_groups_for_user_view, name='get_study_groups_for_user'),
    path('studygroups/<str:group_id>/remove/<str:user_id>/', views.remove_user_from_study_group_view, name='remove_user_from_study_group'),
    path('studygroups/<str:group_id>/delete/', views.delete_study_group_view, name='delete_study_group'),
    path('recommend-partners/<str:user_id>/', views.recommend_study_partners_view, name='recommend_study_partners'),
]