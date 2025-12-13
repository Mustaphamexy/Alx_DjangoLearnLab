# posts/serializers.py

from rest_framework import serializers
from .models import Post, Comment
from django.contrib.contenttypes.models import ContentType
from .models import Like


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'author_username', 'content',
            'created_at', 'updated_at', 'like_count', 'is_liked'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'post']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'title', 'content', 'image',
            'created_at', 'updated_at', 'likes', 'comments',
            'comment_count', 'like_count', 'is_liked'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'likes']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

class LikeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'user_username', 'user_profile_picture', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_user_profile_picture(self, obj):
        if obj.user.profile_picture:
            return obj.user.profile_picture.url
        return None

class LikeCreateSerializer(serializers.Serializer):
    content_type = serializers.CharField(required=True)
    object_id = serializers.IntegerField(required=True)
    
    def validate(self, data):
        # Validate content_type
        try:
            content_type = ContentType.objects.get(model=data['content_type'])
            data['content_type'] = content_type
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid content type")
        
        # Validate object exists
        model_class = content_type.model_class()
        try:
            obj = model_class.objects.get(id=data['object_id'])
            data['object'] = obj
        except model_class.DoesNotExist:
            raise serializers.ValidationError("Object does not exist")
        
        return data