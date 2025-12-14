# notifications/models.py

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('post', 'New Post'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actor_notifications'
    )
    verb = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Generic foreign key for the target object (post, comment, etc.)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='target_notifications'
    )
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')
    
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)  # Changed from created_at to timestamp
    created_at = models.DateTimeField(auto_now_add=True)  # Keep both for compatibility
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['recipient', 'read', 'timestamp']),
            models.Index(fields=['recipient', 'notification_type']),
        ]
    
    def __str__(self):
        return f"{self.actor.username} {self.verb}"
    
    def mark_as_read(self):
        self.read = True
        self.save()
    
    def mark_as_unread(self):
        self.read = False
        self.save()
    
    @classmethod
    def create_like_notification(cls, recipient, actor, target):
        """Create notification for likes"""
        content_type = ContentType.objects.get_for_model(target)
        if content_type.model == 'post':
            verb = 'liked your post'
        elif content_type.model == 'comment':
            verb = 'liked your comment'
        else:
            verb = 'liked your content'
        
        return cls.objects.create(
            recipient=recipient,
            actor=actor,
            verb=verb,
            notification_type='like',
            target_content_type=content_type,
            target_object_id=target.id,
            timestamp=timezone.now()
        )
    
    @classmethod
    def create_comment_notification(cls, recipient, actor, target, comment_text=None):
        """Create notification for comments"""
        return cls.objects.create(
            recipient=recipient,
            actor=actor,
            verb=f'commented on your post: "{comment_text[:50]}..."' if comment_text else 'commented on your post',
            notification_type='comment',
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.id,
            timestamp=timezone.now()
        )
    
    @classmethod
    def create_follow_notification(cls, recipient, actor):
        """Create notification for follows"""
        return cls.objects.create(
            recipient=recipient,
            actor=actor,
            verb='started following you',
            notification_type='follow',
            timestamp=timezone.now()
        )
    
    @classmethod
    def create_post_notification(cls, recipient, actor, target):
        """Create notification for new posts from followed users"""
        return cls.objects.create(
            recipient=recipient,
            actor=actor,
            verb='posted something new',
            notification_type='post',
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.id,
            timestamp=timezone.now()
        )