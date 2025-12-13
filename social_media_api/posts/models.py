# posts/models.py

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(
        upload_to='posts/images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    @property
    def like_count(self):
        """Get the number of likes on this post"""
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Post),
            object_id=self.id
        ).count()
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    def user_has_liked(self, user):
        """Check if a user has liked this post"""
        if not user.is_authenticated:
            return False
        return Like.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=self.id
        ).exists()

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    @property
    def like_count(self):
        """Get the number of likes on this comment"""
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id
        ).count()
    
    def user_has_liked(self, user):
        """Check if a user has liked this comment"""
        if not user.is_authenticated:
            return False
        return Like.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id
        ).exists()

class Like(models.Model):
    """Model to track likes on posts and comments"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    
    # Generic foreign key to allow liking both posts and comments
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} liked {self.content_object}"