from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .db import create_study_group, get_study_group, add_user_to_study_group, get_study_groups_for_user, remove_user_from_study_group, delete_study_group
from .serializers import StudyGroupSerializer
from core.db import get_user_by_email, get_potential_study_partners
from core.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.conf import settings
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

# swagger
@swagger_auto_schema(
    method='post',
    operation_summary="Create a study group",
    operation_description="Creates a new study group with the specified name, description, and members.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'member_emails'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the study group"),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description of the study group"),
            'member_emails': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of email addresses of members to be added to the group"
            ),
        },
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Response('Study group created', StudyGroupSerializer),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Create your views here.

# Api view to create a new study group.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_group_view(request):
    name = request.data.get('name')
    description = request.data.get('description')
    member_emails = request.data.get('member_emails')
    creator_id = str(request.user.id)
    if not name or not member_emails:
        return Response({"error": "Missing required fields: 'name' or 'member_emails.'"}, status=status.HTTP_400_BAD_REQUEST)
    if not hasattr(member_emails, '__iter__'):
        return Response({"error": "'member_emails' must be a list or iterable."}, status=status.HTTP_400_BAD_REQUEST)
    member_ids = []
    for email in member_emails:
        user = get_user_by_email(email)
        if user:
            member_ids.append(str(user["_id"]))
        else:
            return Response({"error": f"User with email '{email}' not found"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        group_id = create_study_group(name, description, member_ids, creator_id)
        return Response({"message": "Study group created", "group_id": group_id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error in create_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Get a study group by ID",
    operation_description="Retrieves a study group by its ID.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the study group", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: StudyGroupSerializer,
        status.HTTP_404_NOT_FOUND: "Study group not found",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# Api view to retrieve a study group by their ID.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_group_view(request, group_id):
    try:
        group = get_study_group(group_id)
        if group:
            serializer = StudyGroupSerializer(group)
            return Response(serializer.data)
        else:
            return Response({"error": "Study group not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# swagger
@swagger_auto_schema(
    method='post',
    operation_summary="Add user to study group",
    operation_description="Adds a user to a specific study group.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the study group", type=openapi.TYPE_STRING, required=True),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_email'],
        properties={
            'user_email': openapi.Schema(type=openapi.TYPE_STRING, description="Email of the user to add"),
        },
    ),
    responses={
        status.HTTP_200_OK: "User added to study group",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_404_NOT_FOUND: "User not found",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Api view to add a user to a study group.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_study_group_view(request, group_id):
    user_email = request.data.get('user_email')
    admin_email = request.user.email 
    if not user_email:
        return Response({"error": "Missing required field: 'user_email'"}, status=status.HTTP_400_BAD_REQUEST)
    admin = get_user_by_email(admin_email)
    if not admin:
        return Response({"error": f"Admin user with email '{admin_email}' not found"}, status=status.HTTP_404_NOT_FOUND)
    user = get_user_by_email(user_email)
    if not user:
        return Response({"error": f"User with email '{user_email}' not found"}, status=status.HTTP_404_NOT_FOUND)
    user_id = str(user["_id"])
    admin_id = str(admin["_id"])
    try:
        success = add_user_to_study_group(group_id, user_id, admin_id)
        if success:
            return Response({"message": "User added to study group"})
        else:
            return Response({"error": "Failed to add user to study group"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in add_user_to_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Get study groups for user",
    operation_description="Retrieves all study groups for a specific user.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: StudyGroupSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# Api view to retrieve all study groups for that user.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_groups_for_user_view(request, user_id):
    try:
        groups = get_study_groups_for_user(user_id)
        serializer = StudyGroupSerializer(groups, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_study_groups_for_user_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

# Api view to recommend potential study partners for a user.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_study_partners_view(request, user_id):
    if str(request.user.id) != user_id:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        potential_partners = get_potential_study_partners(user_id)
        serializer = UserSerializer(potential_partners, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in recommend_study_partners_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# swagger
@swagger_auto_schema(
    method='post',
    operation_summary="Remove user from study group",
    operation_description="Removes a user from a specific study group.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the study group", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user to remove", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: "User removed from study group",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Api view to remove a user from that study group.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_user_from_study_group_view(request, group_id, user_id):
    admin_email = request.user.email
    admin = get_user_by_email(admin_email)
    if not admin:
        return Response({"error": f"Admin user with email '{admin_email}' not found"}, status=status.HTTP_404_NOT_FOUND)
    admin_id = str(admin["_id"])
    try:
        success = remove_user_from_study_group(group_id, user_id, admin_id)
        if success:
            return Response({"message": "User removed from study group"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to remove user from study group"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in remove_user_from_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# swagger
@swagger_auto_schema(
    method='delete',
    operation_summary="Delete study group",
    operation_description="Deletes a specific study group.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the study group to delete", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: "Study group deleted",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Api view to delete the study group.
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_study_group_view(request, group_id):
    try:
        success = delete_study_group(group_id)
        if success:
            return Response({"message": "Study group deleted"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to delete study group"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in delete_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)