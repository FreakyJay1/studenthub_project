from urllib import response
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.http import response
from .db import create_user, get_user_by_email, get_potential_study_partners
from .models import User
from .forms import RegistrationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
import json
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


logger = logging.getLogger(__name__)

# swagger
@swagger_auto_schema(
    method='post',
    operation_description="Registers a new user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password', 'first_name', 'last_name'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'favorite_programming_languages': openapi.Schema(type=openapi.TYPE_STRING, description="e.g., Python, JavaScript"),
            'favorite_path': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="e.g., Mobile Development, Blockchain"
            ),
            'preferred_learning_style': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="e.g., Visual, Auditory"
            ),
            'participate_in_events': openapi.Schema(type=openapi.TYPE_STRING, enum=["Yes", "No"]),
            'receive_recommendations': openapi.Schema(type=openapi.TYPE_STRING, enum=["Yes", "No"]),
            'study_preference': openapi.Schema(type=openapi.TYPE_STRING, enum=["Group", "Solo"]),
            'important_features': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="e.g., Upcoming deadlines, Course materials"
            ),
            'most_used_tool': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="e.g., VS Code, GitHub"
            ),
        },
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Response('User registered and logged in successfully', UserSerializer),
        status.HTTP_400_BAD_REQUEST: openapi.Response('Bad request (e.g., invalid JSON, missing fields, form errors)'),
        status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal server error'),
    }
)

# Create your views here.
@api_view(['POST'])
def register_view(request):
    # Checks if the request method is POST
    if request.method == 'POST':
        data = request.data
    
        # Use the form to validate the data.
        form = RegistrationForm(data)
        if not form.is_valid():
            return response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Creating user in the database.
        try:
            user = User.objects.create_user(
                username=data['email'],
                password=data['password'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            user.save()
        except Exception as e:
            logger.error(f"Error creating user in Django's auth system: {e}")
            return response({"error": "Failed to create user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            return response({"error": "Failed to store user data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Authenticate and log in the user.
        user = authenticate(request, username=data['email'], password=data['password'])
        if user is not None:
            login(request, user)
            return response({"message": "User registered and logged in successfully", "redirect_url": "/dashboard/"}, status=status.HTTP_201_CREATED)
        else:
            logger.error("Failed to log in user after registration")
            return response({"error": "Failed to log in user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# swagger
@swagger_auto_schema(
    method='post',
    operation_description="Logs in an existing user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        status.HTTP_200_OK: openapi.Response('Login successful', UserSerializer),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# Handling user login request.
@api_view(['POST'])
def login_view(request):
    # Checks if the request method is POST
    if request.method != 'POST':
        return response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    data = request.data
    
    # Handles the user authentication and login process.
    email = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return response({"message": "Login successful", "redirect_url": "/dashboard/"}, status=status.HTTP_200_OK)
    else:
        return response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Recommend study partners",
    operation_description="Recommends potential study partners for a given user.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user for whom to recommend partners", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: UserSerializer(many=True),
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# That is responsible for recommending potential study partners
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_study_partners_view(request, user_id):
    if str(request.user.id) != user_id:
        return response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        potential_partners = get_potential_study_partners(user_id)
        serializer = UserSerializer(potential_partners, many=True)
        return response(serializer.data)
    except Exception as e:
        logger.error(f"Error in recommend_study_partners_view: {e}")
        return response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)