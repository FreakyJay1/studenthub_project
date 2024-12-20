from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .db import get_group_conversation
from datetime import datetime
import json

# Celery task to send a group message to all members of that group.
@shared_task
def send_group_message_task(group_id, message_id, sender_id, content):
    group_info = get_group_conversation(group_id)
    if not group_info:
        return
    channel_layer = get_channel_layer()
    for member_id in group_info['members']:
        member_id_str = str(member_id)
        # Sending a message to all members of a group
        async_to_sync(channel_layer.group_send)(
            f'chat_{member_id_str}',
            {
                'type': 'group_chat_message',
                'message': {
                    '_id': message_id,
                    'group_id': group_id,
                    'sender_id': sender_id,
                    'content': content,
                    'timestamp': datetime.now().isoformat(),
                    'read_by': []
                }
            }
        )

# Celery task to send a private message to that specific user.
@shared_task
def send_private_message_task(sender_id, receiver_id, content, message_id):
    channel_layer = get_channel_layer()
    
    # Send message to receiver
    async_to_sync(channel_layer.group_send)(
        f'chat_{receiver_id}',
        {
            'type': 'chat_message',
            'message': {
                '_id': message_id,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'read': False
            }
        }
    )