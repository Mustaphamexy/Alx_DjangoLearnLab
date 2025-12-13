# notifications/urls.py

from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    MarkAllNotificationsReadView,
    DeleteAllNotificationsView,
    NotificationCountView,
    UnreadNotificationsView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread/', UnreadNotificationsView.as_view(), name='unread-notifications'),
    path('count/', NotificationCountView.as_view(), name='notification-count'),
    path('mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark-all-read'),
    path('delete-all/', DeleteAllNotificationsView.as_view(), name='delete-all'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
]