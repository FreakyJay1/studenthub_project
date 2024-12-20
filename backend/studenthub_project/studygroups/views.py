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

logger = logging.getLogger(__name__)

# Create your views here.

# Api view to create a new study group.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_group(request):
    name = request.data.get('name')
    description = request.data.get('description')
    member_emails = request.data.get('member_emails')
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
        group_id = create_study_group(name, description, member_ids)
        return Response({"message": "Study group created", "group_id": group_id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error in create_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

# Api view to add a user to a study group.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_study_group_view(request, group_id):
    user_email = request.data.get('user_email')
    if not user_email:
        return Response({"error": "Missing required field: 'user_email'"}, status=status.HTTP_400_BAD_REQUEST)
    user = get_user_by_email(user_email)
    if not user:
        return Response({"error": f"User with email '{user_email}' not found"}, status=status.HTTP_404_NOT_FOUND)
    user_id = str(user["_id"])
    try:
        success = add_user_to_study_group(group_id, user_id)
        if success:
            return Response({"message": "User added to study group"})
        else:
            return Response({"error": "Failed to add user to study group"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in add_user_to_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

# Api view to remove a user from that study group.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_user_from_study_group_view(request, group_id, user_id):
    try:
        success = remove_user_from_study_group(group_id, user_id)
        if success:
            return Response({"message": "User removed from study group"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to remove user from study group"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in remove_user_from_study_group_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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