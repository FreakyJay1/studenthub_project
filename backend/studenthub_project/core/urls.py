from django.urls import path
from . import views

urlpatterns = [
    path('api/core/register/', views.register_view, name='register'),
    path('api/core/login/', views.login_view, name='login'),
]