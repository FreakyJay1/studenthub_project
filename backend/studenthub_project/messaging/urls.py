from django.urls import path
from . import views

urlpatterns = [
    path('messages/<str:user_id1>/<str:user_id2>/', views.get_messages_between_users_view, name='get_messages_between_users'),
    path('messages/<str:user_id>/', views.get_all_messages_for_user_view, name='get_all_messages_for_user'),
    path('messages/<str:user_id>/search/', views.search_messages_for_user_view, name='search_messages_for_user'),
    path('messages/<str:user_id>/groupsearch/', views.search_group_messages_for_user_view, name='search_group_messages_for_user'),
    path('groups/', views.create_group_conversation_view, name='create_group_conversation'),
    path('groups/<str:group_id>/messages/', views.get_messages_for_group_conversation_view, name='get_messages_for_group_conversation'),
    path('groups/<str:group_id>/add/', views.add_user_to_group_conversation_view, name='add_user_to_group_conversation'),
    path('groups/<str:group_id>/remove/<str:user_id>/', views.remove_user_from_group_conversation_view, name='remove_user_from_group_conversation'),
    path('groups/<str:group_id>/delete/', views.delete_group_conversation_view, name='delete_group_conversation'),
    path('notifications/<str:user_id>/', views.get_notifications_for_user_view, name='get_notifications_for_user'),
]