from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.db import get_user_by_email
from .db import add_message_to_group_conversation, create_message, delete_group_conversation, get_messages_between_users, get_all_messages_for_user, create_group_conversation, get_messages_for_group_conversation, add_user_to_group_conversation, remove_user_from_group_conversation, get_notifications_for_user, get_group_conversation, search_group_messages_for_user, search_messages_for_user
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
        required=['group_name', 'member_emails'],
        properties={
            'group_name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the group"),
            'member_emails': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of user emails to be added to the group"
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
def create_group_conversation_view(request):
    try:
        group_name = request.data.get('group_name')
        member_emails = request.data.get('member_emails')
        if not group_name or not member_ids:
            return Response({"error": "Missing 'group_name' or 'member_ids'"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle member_ids as a list, even if it's a single ID or another iterable
        if not hasattr(member_ids, '__iter__') and not isinstance(member_emails, str):
            try:
                member_ids = list(member_emails)
            except Exception:
                return Response({"error": "Failed to convert 'member_ids' to a list"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            member_ids = [member_emails]
        
        member_ids = []
        for email in member_emails:
            user = get_user_by_email(email)
            if user:
                member_ids.append(str(user["_id"]))
            else:
                return Response({"error": f"User with email '{email}' not found"}, status=status.HTTP_400_BAD_REQUEST)
        creater_id = str(request.user.id)
        group_id = create_group_conversation(group_name, member_ids, creater_id)
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
    operation_description="Adds a user to an existing group conversation, requires admin privileges.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group conversation", type=openapi.TYPE_STRING, required=True),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_email'],
        properties={
            'user_email': openapi.Schema(type=openapi.TYPE_STRING, description="Email of the user to add"),
            'admin_email': openapi.Schema(type=openapi.TYPE_STRING, description="Email of the group admin"),
        },
    ),
    responses={
        status.HTTP_200_OK: "User added to group conversation",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden (not an admin)",
        status.HTTP_404_NOT_FOUND: "User or group not found",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Adding user to group conversation.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_group_conversation_view(request, group_id):
    user_email = request.data.get('user_email')
    admin_email = request.data.get('admin_email')
    if not user_email or not admin_email:
        return Response({"error": "Missing required field: 'user_email' or 'admin_email"}, status=status.HTTP_400_BAD_REQUEST)
    admin = get_user_by_email(admin_email)
    if not admin:
        return Response({"error": f"Admin user with email '{admin_email}' not found"}, status=status.HTTP_404_NOT_FOUND)
    group = get_group_conversation(group_id)
    if not group or str(group.get('created_by')) != str(admin['_id']):
        return Response({"error": "Unauthorized to add user to this group"}, status=status.HTTP_403_FORBIDDEN)
    user = get_user_by_email(user_email)
    if not user:
        return Response({"error": f"User with email '{user_email}' not found"}, status=status.HTTP_404_NOT_FOUND)
    user_id = str(user["_id"])
    admin_id = str(admin["_id"])
    try:
        success = add_user_to_group_conversation(group_id, user_id, admin_id)
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
    operation_description="Removes a user from a group conversation, requires admin privileges.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group conversation", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user to remove", type=openapi.TYPE_STRING, required=True),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['admin_email'],
        properties={
            'admin_email': openapi.Schema(type=openapi.TYPE_STRING, description="Email of the group admin"),
        },
    ),
    responses={
        status.HTTP_200_OK: "User removed from group conversation",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden (not an admin)",
        status.HTTP_404_NOT_FOUND: "User or group not found",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Removing user from group conversation.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_user_from_group_conversation_view(request, group_id, user_id):
    admin_email = request.data.get('admin_email')
    if not admin_email:
        return Response({"error": "Missing required field: 'admin_email'"}, status=status.HTTP_400_BAD_REQUEST)
    admin = get_user_by_email(admin_email)
    if not admin:
        return Response({"error": f"Admin user with email '{admin_email}' not found"}, status=status.HTTP_404_NOT_FOUND)
    group = get_group_conversation(group_id)
    if not group or str(group.get('created_by')) != str(admin['_id']):
        return Response({"error": "Unauthorized to remove user from this group"}, status=status.HTTP_403_FORBIDDEN)
    admin_id = str(admin["_id"])
    try:
        success = remove_user_from_group_conversation(group_id, user_id, admin_id)
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

# Swagger
@swagger_auto_schema(
    method='delete',
    operation_summary="Delete group conversation",
    operation_description="Deletes a group conversation and all its messages by group ID.",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group conversation to delete", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_204_NO_CONTENT: "Group conversation deleted successfully",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden",
        status.HTTP_404_NOT_FOUND: "Group conversation not found",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Api view to delete a group conversation and all it is messages.
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_group_conversation_view(request, group_id):
    try:
        group = get_group_conversation(group_id)
        if not group:
            return Response({"error": "Group conversation not found"}, status=status.HTTP_404_NOT_FOUND)
        if str(request.user.id) != str(group['created_by']):
            return Response({"error": "Unauthorized to delete this group conversation"}, status=status.HTTP_403_FORBIDDEN)
        success = delete_group_conversation(group_id)
        if success:
            return Response({"message": "Group conversation deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Failed to delete group conversation"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in delete_group_conversation_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Search messages for a user",
    operation_description="Searches messages sent or received by a specific user for a query string.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('query', openapi.IN_QUERY, description="Search query string", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: MessageSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# Api view for search messages in user view.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages_for_user_view(request, user_id):
    query_string = request.query_params.get('query', '')
    try:
        messages = search_messages_for_user(user_id, query_string)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in search_messages_for_user_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Swagger
@swagger_auto_schema(
    method='get',
    operation_summary="Search group messages for a user",
    operation_description="Searches group messages for a specific user for a query string.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('query', openapi.IN_QUERY, description="Search query string", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: GroupMessageSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# Api view for search messages in user group messages.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_group_messages_for_user_view(request, user_id):
    query_string = request.query_params.get('query', '')
    try:
        messages = search_group_messages_for_user(user_id, query_string)
        serializer = GroupMessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in search_group_messages_for_user_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Swagger.
@swagger_auto_schema(
    method='post',
    operation_summary="Share resource in private message",
    operation_description="Shares a resource in a private message.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['receiver_email', 'resource_id'],
        properties={
            'receiver_email': openapi.Schema(type=openapi.TYPE_STRING, description="Email of the receiver"),
            'resource_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the resource to share"),
            'message_content': openapi.Schema(type=openapi.TYPE_STRING, description="Optional message content"),
        },
    ),
    responses={
        status.HTTP_200_OK: MessageSerializer,
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_404_NOT_FOUND: "Receiver not found",
    }
)

# API view for to share resource in private chats.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_resource_private_view(request):
    sender_id = str(request.user.id)
    receiver_email = request.data.get('receiver_email')
    resource_id = request.data.get('resource_id')
    message_content = request.data.get('message_content', "")
    receiver = get_user_by_email(receiver_email)
    if not receiver:
        return Response({"error": "Receiver not found"}, status=status.HTTP_404_NOT_FOUND)
    receiver_id = str(receiver["_id"])
    message_id = create_message(sender_id, receiver_id, message_content, resource_id)
    if message_id:
        return Response({"message": "Resource shared successfully", "message_id": message_id}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to share resource"}, status=status.HTTP_400_BAD_REQUEST)

# Swagger.
@swagger_auto_schema(
    method='post',
    operation_summary="Share resource in group",
    operation_description="Shares a resource in a group conversation.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['group_id', 'resource_id'],
        properties={
            'group_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the group conversation"),
            'resource_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the resource to share"),
            'message_content': openapi.Schema(type=openapi.TYPE_STRING, description="Optional message content"),
        },
    ),
    responses={
        status.HTTP_200_OK: GroupMessageSerializer,
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_404_NOT_FOUND: "Group not found",
    }
)

# API view for to share resource in group chats.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_resource_group_view(request):
    sender_id = str(request.user.id)
    group_id = request.data.get('group_id')
    resource_id = request.data.get('resource_id')
    message_content = request.data.get('message_content', "")
    group_info = get_group_conversation(group_id)
    if not group_info:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
    message_id = add_message_to_group_conversation(group_id, sender_id, message_content, resource_id)
    if message_id:
        return Response({"message": "Resource shared in group", "message_id": message_id}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to share resource in group"}, status=status.HTTP_400_BAD_REQUEST)
