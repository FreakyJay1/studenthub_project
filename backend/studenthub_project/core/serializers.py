from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 
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
        
        # Converting 'important_features' to a list when it is serializing.
        def to_representation(self, instance):
            data = super().to_representation(instance)
            if data['important_features']:
                data['important_features'] = data['important_features']
            return data
        
        # Converting 'important_features' to comma-separated string when it is deserializing.
        def to_internal_value(self, data):
            if 'important_features' in data:
                if hasattr(data['important_features'], 'split'):
                    data['important_features'] = data['important_features'].split(',')
                elif not hasattr(data['important_features'], '__iter__'):
                    raise serializers.ValidationError({'important_features': 'Must be a list or a string.'})
            return super().to_internal_value(data)