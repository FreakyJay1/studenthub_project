from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',  
            'email', 
            'first_name', 
            'last_name',
            'favorite_programming_languages',
            'favorite_path',
            'preferred_learning_style',
            'participate_in_events',
            'receive_recommendations',
            'study_preference',
            'important_features',
            'most_used_tool'
        ]
        read_only_fields = ('id',)