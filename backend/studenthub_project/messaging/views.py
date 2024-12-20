from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .db import get_messages_between_users, get_all_messages_for_user, create_group_conversation, get_messages_for_group_conversation, add_user_to_group_conversation, remove_user_from_group_conversation, get_notifications_for_user, get_group_conversation
from .serializers import GroupMessageSerializer, MessageSerializer, NotificationSerializer, GroupConversationSerializer
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

# swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Get messages between two users",
    operation_description="Retrieves messages exchanged between two users.",
    manual_parameters=[
        openapi.Parameter('user_id1', openapi.IN_PATH, description="ID of the first user", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('user_id2', openapi.IN_PATH, description="ID of the second user", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: MessageSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# Create your views here.

# To fecth messages exchanged between user 1 and user 2.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages_between_users_view(request,user_id1, user_id2):
    try:
        messages = get_messages_between_users(user_id1,user_id2)
        serializer = MessageSerializer(messages,many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_messages_between_users_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Get all messages for a user",
    operation_description="Retrieves all messages (sent and received) for a specific user.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: MessageSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# To fecth all messages for the specified user.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_messages_for_user_view(request, user_id):
    try:
        messages = get_all_messages_for_user(user_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_all_messages_for_user_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# swagger
@swagger_auto_schema(
    method='post',
    operation_summary="Create a group conversation",
    operation_description="Creates a new group conversation with the specified name and members.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['group_name', 'member_ids'],
        properties={
            'group_name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the group"),
            'member_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of user IDs to be added to the group"
            ),
        },
    ),
    responses={
        status.HTTP_201_CREATED: GroupConversationSerializer,
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# To create a group conversation.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group_conversation(request):
    try:
        group_name = request.data.get('group_name')
        member_ids = request.data.get('member_ids')
        if not group_name or not member_ids:
            return Response({"error": "Missing 'group_name' or 'member_ids'"}, status=status.HTTP_400_BAD_REQUEST)
        if not hasattr(member_ids, '__iter__'):
            try:
                member_ids = list(member_ids)
            except Exception:
                return Response({"error": "Failed to convert 'member_ids' to a list"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            member_ids = [member_ids]
        group_id = create_group_conversation(group_name, member_ids)
        if group_id:
            return Response({"message": "Group conversation created", "group_id": group_id}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to create group conversation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error in create_group_conversation_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Get messages for a group conversation",
    operation_description="Retrieves all messages for a specific group conversation.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group conversation", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: GroupMessageSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# To get group conversation messages.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages_for_group_conversation_view(request, group_id):
    try:
        messages = get_messages_for_group_conversation(group_id)
        serializer = GroupMessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_messages_for_group_conversation_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# swagger
@swagger_auto_schema(
    method='post',
    operation_summary="Add user to group conversation",
    operation_description="Adds a user to an existing group conversation.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group conversation", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user to add", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: "OK",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Adding user to group conversation.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_group_conversation_view(request, group_id, user_id):
    try:
        success = add_user_to_group_conversation(group_id, user_id)
        if success:
            return Response({"message": "User added to group conversation"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to add user to group"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in add_user_to_group_conversation_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# swagger
@swagger_auto_schema(
    method='post',
    operation_summary="Remove user from group conversation",
    operation_description="Removes a user from a group conversation.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group conversation", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user to remove", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: "OK",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Removing user from group conversation.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_user_from_group_conversation_view(request, group_id, user_id):
    try:
        success = remove_user_from_group_conversation(group_id, user_id)
        if success:
            return Response({"message": "User removed from group conversation"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to remove user from group"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in remove_user_from_group_conversation_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Get notifications for a user",
    operation_description="Retrieves all notifications for a specific user.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: NotificationSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# To get the notification.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications_for_user_view(request, user_id):
    try:
        notifications = get_notifications_for_user(user_id)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_notifications_for_user_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)