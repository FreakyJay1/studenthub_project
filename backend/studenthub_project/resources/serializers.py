from rest_framework import serializers

class ResourceSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    location = serializers.DictField(required=False, child=serializers.CharField())
    hours = serializers.DictField(child=serializers.DictField(required=False))
    contact = serializers.DictField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    created_by = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    
    # Validate the link field to ensure it's a valid URL.
    def validate_link(self, value):
        if not value.startswith("http://") and not value.startswith("https://"):
            raise serializers.ValidationError("Invalid URL format.")
        return value