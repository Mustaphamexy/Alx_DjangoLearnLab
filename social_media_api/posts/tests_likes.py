# posts/tests_likes.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from accounts.models import CustomUser
from posts.models import Post, Comment, Like
from notifications.models import Notification

class LikeTests(APITestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        self.post = Post.objects.create(
            author=self.user1,
            title='Test Post',
            content='Test Content'
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user2,
            content='Test Comment'
        )
        
        self.client.force_authenticate(user=self.user2)
    
    def test_like_post(self):
        """Test liking a post"""
        url = reverse('like-post', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Post liked successfully')
        self.assertEqual(self.post.like_count, 1)
        
        # Check if like was created
        content_type = ContentType.objects.get_for_model(Post)
        self.assertTrue(Like.objects.filter(
            user=self.user2,
            content_type=content_type,
            object_id=self.post.id
        ).exists())
        
        # Check if notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.actor, self.user2)
        self.assertEqual(notification.notification_type, 'like')
    
    def test_like_own_post_no_notification(self):
        """Test that liking own post doesn't create notification"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('like-post', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.like_count, 1)
        self.assertEqual(Notification.objects.count(), 0)  # No notification for own like
    
    def test_like_post_twice_fails(self):
        """Test that liking a post twice fails"""
        url = reverse('like-post', kwargs={'post_id': self.post.id})
        
        # First like
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second like should fail
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already liked', response2.data['error'])
    
    def test_unlike_post(self):
        """Test unliking a post"""
        # First like the post
        content_type = ContentType.objects.get_for_model(Post)
        Like.objects.create(
            user=self.user2,
            content_type=content_type,
            object_id=self.post.id
        )
        
        url = reverse('unlike-post', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Post unliked successfully')
        self.assertEqual(self.post.like_count, 0)
    
    def test_like_comment(self):
        """Test liking a comment"""
        url = reverse('like-comment', kwargs={'comment_id': self.comment.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Comment liked successfully')
        self.assertEqual(self.comment.like_count, 1)
    
    def test_get_post_likes_list(self):
        """Test getting list of users who liked a post"""
        # Create some likes
        user3 = CustomUser.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        content_type = ContentType.objects.get_for_model(Post)
        Like.objects.create(user=self.user2, content_type=content_type, object_id=self.post.id)
        Like.objects.create(user=user3, content_type=content_type, object_id=self.post.id)
        
        url = reverse('post-likes-list', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        usernames = [like['user_username'] for like in response.data['results']]
        self.assertIn('user2', usernames)
        self.assertIn('user3', usernames)