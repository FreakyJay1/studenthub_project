from rest_framework import serializers

class CourseSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    link = serializers.CharField()

    # Validate the link field to ensure it's a valid URL.
    def validate_link(self, value):
        if not value.startswith("http://") and not value.startswith("https://"):
            raise serializers.ValidationError("Invalid URL format.")
        return value