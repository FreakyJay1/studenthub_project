from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from.db import create_user, get_user_email
from django.http import JsonResponse
from .models import User
import json
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Create your views here.

def register_view(request):
    # It is ensuing that my backend can correctly recieve and process JSON data,
    # that was sent by user from frontend.
    
    if request.method == 'POST':
        try:
            data = json.load(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status = 400)
        
        # Extracting and Validating the required fields for database.
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        favorite_programming_languages = data.get('favorite_programming_languages')
        favorite_path = ",".join(data.get('favorite_path', []))
        preferred_learning_style = ",".join(data.get('preferred_learning_style', []))
        participate_in_events = data.get('participate_in_events')
        receive_recommendations = data.get('receive_recommendations')
        study_preference = data.get('study_preference')
        important_features = ",".join(data.get('important_features', []))
        most_used_tool = ",".join(data.get('most_used_tool', []))
        
        errors = {}
        
        # Validations
        
        require_fields = [
            'email', 'password', 'first_name', 'last_name',
            'favorite_programming_languages', 'favorite_path',
            'preferred_learning_style', 'study_preference',
            'important_features', 'most_used_tool'
        ]
        
        for field in require_fields:
            if not data.get(field):
                errors[field] = ["This field is required to process."]
                
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors["email"] = ["Enter a valid email address to process."]
                
        if email and get_user_email(email):
            errors["email"] = ["Email already exists in the database."]
            
        if password and len(password) < 8:
            errors["password"] = ["Password must be at least 8 characters long to process."]
        
        allowed_study_preferences = ["Group", "Solo"]
        if data.get('study_preference') not in allowed_study_preferences:
            errors["study_preference"] = ["Invalid study preference."]

        if data.get('participate_in_events') is not None and data.get('participate_in_events') not in ["Yes", "No"]:
            errors["participate_in_events"] = ["Must be Yes or No."]

        if data.get('receive_recommendations') is not None and data.get('receive_recommendations') not in ["Yes", "No"]:
            errors["receive_recommendations"] = ["Must be Yes or No."]
            
        if errors:
            return JsonResponse({"errors":errors}, status=400)
        
        # Creating user in the Django's auth system.
        try:
            user = User.objects.create_user(
                username=email,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        # Storing additional user data in the database.
        user_data = {
            "username": email,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "favorite_programming_languages": favorite_programming_languages,
            "favorite_path": favorite_path,
            "preferred_learning_style": preferred_learning_style,
            "participate_in_events": participate_in_events,
            "receive_recommendations": receive_recommendations,
            "study_preference": study_preference,
            "important_features": important_features,
            "most_used_tool": most_used_tool,
        }
        create_user(user_data)
        
        # Authenticate and Log in for the user.
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "User registered and logged in successfully", "redirect_url": "/dashboard/"})
        else:
            return JsonResponse({"error": "Failed to log in user"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
# Handling user login request.
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Login successfully", "redirect_url": "/dashboard/"})
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)