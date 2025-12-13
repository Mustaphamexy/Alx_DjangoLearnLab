# notifications/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from .models import Notification
from .serializers import (
    NotificationSerializer, 
    NotificationUpdateSerializer,
    NotificationCountSerializer
)

class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class NotificationListView(generics.ListAPIView):
    """View to list all notifications for the authenticated user"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor', 'recipient').order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        # Mark notifications as read when viewed
        if request.query_params.get('mark_read', 'false').lower() == 'true':
            unread_notifications = Notification.objects.filter(
                recipient=request.user,
                read=False
            )
            unread_notifications.update(read=True)
        
        return super().get(request, *args, **kwargs)

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete a specific notification"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def perform_destroy(self, instance):
        # Only allow deleting own notifications
        if instance.recipient == self.request.user:
            instance.delete()

class MarkAllNotificationsReadView(APIView):
    """View to mark all notifications as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        updated_count = Notification.objects.filter(
            recipient=request.user,
            read=False
        ).update(read=True)
        
        return Response({
            'message': f'Marked {updated_count} notifications as read',
            'marked_read': updated_count
        }, status=status.HTTP_200_OK)

class DeleteAllNotificationsView(APIView):
    """View to delete all notifications"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        deleted_count, _ = Notification.objects.filter(
            recipient=request.user
        ).delete()
        
        return Response({
            'message': f'Deleted {deleted_count} notifications',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)

class NotificationCountView(APIView):
    """View to get notification counts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        unread_count = Notification.objects.filter(
            recipient=request.user,
            read=False
        ).count()
        
        total_count = Notification.objects.filter(
            recipient=request.user
        ).count()
        
        serializer = NotificationCountSerializer({
            'unread_count': unread_count,
            'total_count': total_count
        })
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class UnreadNotificationsView(generics.ListAPIView):
    """View to list only unread notifications"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
            read=False
        ).select_related('actor', 'recipient').order_by('-created_at')