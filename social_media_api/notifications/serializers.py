# notifications/serializers.py

from rest_framework import serializers
from .models import Notification
from django.contrib.contenttypes.models import ContentType

class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    actor_profile_picture = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()
    target_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'actor', 'actor_username', 'actor_profile_picture',
            'verb', 'notification_type', 'target', 'target_type', 'target_data',
            'read', 'created_at'
        ]
        read_only_fields = ['id', 'recipient', 'actor', 'created_at']
    
    def get_actor_profile_picture(self, obj):
        if obj.actor.profile_picture:
            return obj.actor.profile_picture.url
        return None
    
    def get_target_type(self, obj):
        if obj.target_content_type:
            return obj.target_content_type.model
        return None
    
    def get_target_data(self, obj):
        if not obj.target:
            return None
        
        # Return basic target information
        if hasattr(obj.target, 'title'):
            return {'title': obj.target.title, 'id': obj.target.id}
        elif hasattr(obj.target, 'content'):
            content = obj.target.content[:100] if len(obj.target.content) > 100 else obj.target.content
            return {'content': content, 'id': obj.target.id}
        return {'id': obj.target.id}

class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['read']

class NotificationCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()
    total_count = serializers.IntegerField()