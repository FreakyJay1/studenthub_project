from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from .db import create_user, get_user_by_email
from .models import User
from .forms import RegistrationForm
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@api_view(['POST'])
def register_view(request):
    # Checks if the request method is POST
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Use the form to validate the data.
    form = RegistrationForm(data)
    if not form.is_valid():
        return JsonResponse(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if the email is already use in the database.
    if get_user_by_email(data['email']):
        return JsonResponse({"email": ["This email address is already in use."]}, status=status.HTTP_400_BAD_REQUEST)

    # Creating user in the database.
    try:
        user = User.objects.create_user(
            username=data['email'],  # Use email as username
            password=data['password'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.save()
    except Exception as e:
        logger.error(f"Error creating user in Django's auth system: {e}")
        return JsonResponse({"error": "Failed to create user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Storing additional user data in the database.
    user_data = {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "favorite_programming_languages": data.get("favorite_programming_languages"),
        "favorite_path": data.get("favorite_path"),
        "preferred_learning_style": data.get("preferred_learning_style"),
        "participate_in_events": data.get("participate_in_events"),
        "receive_recommendations": data.get("receive_recommendations"),
        "study_preference": data.get("study_preference"),
        "important_features": data.get("important_features"),
        "most_used_tool": data.get("most_used_tool"),
    }
    try:
        create_user(user_data)
    except Exception as e:
        logger.error(f"Error storing additional user data in MongoDB: {e}")
        return JsonResponse({"error": "Failed to store user data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Authenticate and log in the user.
    user = authenticate(request, username=data['email'], password=data['password'])
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "User registered and logged in successfully", "redirect_url": "/dashboard/"}, status=status.HTTP_201_CREATED)
    else:
        logger.error("Failed to log in user after registration")
        return JsonResponse({"error": "Failed to log in user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Handling user login request.
@api_view(['POST'])
def login_view(request):
    # Checks if the request method is POST
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handles the user authentication and login process.
    email = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "Login successful", "redirect_url": "/dashboard/"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)