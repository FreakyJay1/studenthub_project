from rest_framework import serializers
from bson import ObjectId

# To handle MongoDB's ObjectId type correctly.
class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)
    
    def to_internal_value(self, data):
        try:
            return ObjectId(data)
        except Exception:
            raise serializers.ValidationError("Invalid ObjectID")
        
class MessageSerializer(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    sender_id = ObjectIdField()
    receiver_id = ObjectIdField()
    content = serializers.CharField()
    timestamp = serializers.DateTimeField()
    read = serializers.BooleanField(default=False)
    
class GroupConversationalSerialize(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    group_name = serializers.CharField()
    members = serializers.ListField(child=ObjectIdField())
    created_at = serializers.DateTimeField()
    
class GroupMessageSerialize(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    group_id = ObjectIdField()
    sender_id = ObjectIdField()
    content = serializers.CharField()
    timestamp = serializers.DateTimeField()
    read_by = serializers.ListField(child=ObjectIdField())
    
class NotificationSerialize(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    recipient_id = ObjectIdField()
    message = serializers.CharField()
    is_read = serializers.BooleanField(default=False)
    timestamp = serializers.DateTimeField()