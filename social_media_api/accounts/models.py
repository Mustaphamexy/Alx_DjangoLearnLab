# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

class CustomUser(AbstractUser):
    # ... existing fields ...
    
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    
    # Follow relationships - make sure this is correctly defined
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,  # If A follows B, B doesn't automatically follow A
        related_name='following',  # This creates the reverse relationship
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    @property
    def follower_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.following.count()  # This uses the reverse related name
    
    def is_following(self, user):
        """Check if current user is following the given user"""
        return user in self.following.all()
    
    def is_followed_by(self, user):
        """Check if current user is followed by the given user"""
        return user in self.followers.all()