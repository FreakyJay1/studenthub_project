from django.urls import path
from . import views

urlpatterns = [
    path('resources/', views.get_all_resources_view, name='get_all_resources'),
    path('resources/create/', views.create_resource_view, name='create_resource'),
    path('resources/<resource_id>/', views.get_resource_view, name='get_resource'),
    path('esources/<resource_id>/update/', views.update_resource_view, name='update_resource'),
    path('resources/<resource_id>/delete/', views.delete_resource_view, name='delete_resource'),
    path('resources/search/', views.search_resources_view, name='search_resources'),
]