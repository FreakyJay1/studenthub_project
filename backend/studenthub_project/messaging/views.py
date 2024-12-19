from rest_framework.decorators import api_view
from rest_framework.response import Response
from .db import get_messages_between_users, get_all_messages_for_user, create_group_conversation, get_messages_for_group_conversation, add_user_to_group_conversation, remove_user_from_group_conversation, get_notifications_for_user, get_group_conversation, get_user
from .serializers import GroupMessageSerialize, MessageSerializer, NotificationSerialize
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# Create your views here.

# To fecth messages exchanged between user 1 and user 2.
@api_view(['GET'])
def get_messages_between_users_view(request,user_id1, user_id2):
    try:
        messages = get_messages_between_users(user_id1,user_id2)
        serializer = MessageSerializer(messages,many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

# To fecth all messages for the specified user.
@api_view(['GET'])
def get_all_messages_for_user_view(request, user_id):
    try:
        messages = get_all_messages_for_user(user_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
# To create a group conversation.
@api_view(['POST'])
def create_group_conversation(request):
    try:
        group_name = request.data.get('group_name')
        member_ids = request.data.get('member_ids')
        if not group_name or not member_ids:
            return Response({"error": "Missing 'group_name' or 'member_ids'"}, status=400)
        if not hasattr(member_ids, '__iter__'):
            return Response({"error": "'member_ids' must be iterable"}, status=400)
        group_id = create_group_conversation(group_name, member_ids)
        if group_id:
            return Response({"message": "Group conversation created", "group_id": group_id}, status=201)
        else:
            return Response({"error": "Failed to create group conversation"}, status=500)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
# To get group conversation messages.
@api_view(['GET'])
def get_messages_for_group_conversation_view(request, group_id):
    try:
        messages = get_messages_for_group_conversation(group_id)
        serializer = GroupMessageSerialize(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
# Adding user to group conversation.
@api_view(['POST'])
def add_user_to_group_conversation_view(request, group_id, user_id):
    try:
        success = add_user_to_group_conversation(group_id, user_id)
        if success:
            return Response({"message": "User added to group conversation"})
        else:
            return Response({"error": "Failed to add user to group"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
# Removing user from group conversation.
@api_view(['POST'])
def remove_user_from_group_conversation_view(request, group_id, user_id):
    try:
        success = remove_user_from_group_conversation(group_id, user_id)
        if success:
            return Response({"message": "User removed from group conversation"})
        else:
            return Response({"error": "Failed to remove user from group"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
# To get the notification.
@api_view(['GET'])
def get_notifications_for_user_view(request, user_id):
    try:
        notifications = get_notifications_for_user(user_id)
        serializer = NotificationSerialize(notifications, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)