# notifications/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import CustomUser
from posts.models import Post, Comment
from .models import Notification
from django.contrib.contenttypes.models import ContentType

class NotificationTests(APITestCase):
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
        self.user3 = CustomUser.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        self.post = Post.objects.create(
            author=self.user1,
            title='Test Post',
            content='Test Content'
        )
        
        # Create some notifications
        Notification.create_follow_notification(self.user1, self.user2)
        Notification.create_follow_notification(self.user1, self.user3)
        
        # Create a read notification
        notification = Notification.create_like_notification(
            self.user1,
            self.user2,
            self.post
        )
        notification.mark_as_read()
        
        self.client.force_authenticate(user=self.user1)
    
    def test_get_notifications_list(self):
        """Test getting notifications list"""
        url = reverse('notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_get_unread_notifications(self):
        """Test getting only unread notifications"""
        url = reverse('unread-notifications')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only follow notifications
    
    def test_get_notification_count(self):
        """Test getting notification counts"""
        url = reverse('notification-count')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)
        self.assertEqual(response.data['total_count'], 3)
    
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        url = reverse('mark-all-read')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_read'], 2)
        
        # Check all notifications are now read
        unread_count = Notification.objects.filter(recipient=self.user1, read=False).count()
        self.assertEqual(unread_count, 0)
    
    def test_mark_single_notification_read(self):
        """Test marking a single notification as read"""
        notification = Notification.objects.filter(
            recipient=self.user1,
            read=False
        ).first()
        
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        data = {'read': True}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.read)
    
    def test_delete_all_notifications(self):
        """Test deleting all notifications"""
        url = reverse('delete-all')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 3)
        
        # Check no notifications remain
        self.assertEqual(Notification.objects.filter(recipient=self.user1).count(), 0)