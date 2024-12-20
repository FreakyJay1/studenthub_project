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

class StudyGroupSerializer(serializers.Serializer):
    _id = ObjectIdField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False)
    members = serializers.ListField(child=ObjectIdField())
    created_at = serializers.DateTimeField()