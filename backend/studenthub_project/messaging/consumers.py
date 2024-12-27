import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .db import create_message, get_all_messages_for_user, get_messages_between_users, mark_message_as_read, get_group_conversation, get_messages_for_group_conversation, add_message_to_group_conversation,share_resource_in_group,share_resource_in_message
from core.db import get_user_by_email, get_user
from .serializers import GroupMessageSerialize, MessageSerializer
from datetime import datetime
from bson import ObjectId
from .tasks import send_group_message_task, send_private_message_task
from django.core.cache import cache

# ChatConsumer that inherits from AsyncWebsocketConsumer.
class ChatConsumer(AsyncWebsocketConsumer):
    # This method is called when a Websocket connection is founded.
    async def connect(self):
        self.user_id = str(self.scope['url_route']['kwargs']['user_id'])
        self.group_name = f'chat_{self.user_id}'
        
        # Check if user is authenticated
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        # Adds the consumer's channel to the user's group.
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        # Accepts the WebSocket connection.
        await self.accept()
        # Sends initial messages to the newly connected user.
        await self.send_initial_messages()
    
    # This method is called when Websocket connection is closed.
    async def disconnect(self, close_code):
        # Removes the consumer's channel from the user's group.
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    # This method is called when a message is received from the Websocket.
    async def receive(self, text_data):
        try:
            # Basic Rate Limiting (10 messages per minute per user)
            rate_limit_key = f"rate_limit:{self.user_id}"
            rate_limit_count = cache.get(rate_limit_key, 0)
            if rate_limit_count >= 10:
                await self.send(text_data=json.dumps({
                    'error': 'Rate limit exceeded'
                }))
                return
            cache.set(rate_limit_key, rate_limit_count + 1, timeout=60)
            
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            if message_type == 'private_message':
                await self.handle_private_message(text_data_json)
            elif message_type == 'group_message':
                await self.handle_group_message(text_data_json)
            elif message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Invalid message type'
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Error processing message: {str(e)}'
            }))
    
    # Handles a private message received from a user.
    async def handle_private_message(self, data):
        receiver_email = data['receiver_email']
        content = data['message']
        resource_id = data.get('resource_id')
        receiver = get_user_by_email(receiver_email)
        if not receiver:
            await self.send(text_data=json.dumps({
                'errors': 'Reciever not found'
            }))
            return
        receiver_id = str(receiver["_id"])
        sender_id = self.user_id
        message_id =create_message(sender_id,receiver_id,content,resource_id)
        # Send message to receiver using Celery task
        send_private_message_task.delay(sender_id, receiver_id, content, message_id,resource_id)
        # send confirmation to sender
        await self.send(text_data=json.dumps({
            'type': 'private_message',
            'message': {
                '_id': message_id,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'read': False,
                'resource_id': resource_id
            }
        }))
    
    # Handles a group message received from a user.
    async def handle_group_message(self, data):
        group_id = data['group_id']
        content = data['message']
        resource_id = data.get('resource_id')
        sender_id = self.user_id
        group_info = get_group_conversation(group_id)
        if not group_info:
            await self.send(text_data=json.dumps({
                'error': 'Group not found'
            }))
            return
        message_id = add_message_to_group_conversation(group_id, sender_id, content,resource_id)
        # Use a Celery task to send messages to group members
        send_group_message_task.delay(group_id, message_id, sender_id, content,resource_id)
        # Send confirmation to sender
        await self.send(text_data=json.dumps({
            'type': 'group_message',
            'message': {
                '_id': message_id,
                'group_id': group_id,
                'sender_id': sender_id,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'read_by': [],
                'resource_id': resource_id
            }
        }))
    
    # Handles a request to mark a message as read.
    async def handle_mark_read(self, data):
        message_id = data['message_id']
        mark_message_as_read(message_id)
    
    # This is a message handler function that is called when a message of type chat_message is sent to the group.
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
    
    # This is a message handler function that is called when a message of type group_chat_message is sent to the group.
    async def group_chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
    
    async def send_initial_messages(self):
        messages = get_all_messages_for_user(self.user_id)
        serialized_messages = []
        for message in messages:
            message['_id'] = str(message['_id'])
            if 'sender_id' in message:
                message['sender_id'] = str(message['sender_id'])
            if 'receiver_id' in message:
                message['receiver_id'] = str(message['receiver_id'])
            if 'group_id' in message:
                message['group_id'] = str(message['group_id'])
            if 'read_by' in message:
                message['read_by'] = [str(user_id) for user_id in message['read_by']]
            if 'timestamp' in message:
                message['timestamp'] = message['timestamp'].isoformat()
        await self.send(text_data=json.dumps({'initial_messages': serialized_messages}))