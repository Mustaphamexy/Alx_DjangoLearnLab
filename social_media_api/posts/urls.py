# posts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CommentViewSet, FeedView, PersonalizedFeedView,
    LikePostView, UnlikePostView, LikeCommentView, UnlikeCommentView,
    PostLikesListView
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    
    # Feed endpoints
    path('feed/', FeedView.as_view(), name='feed'),
    path('feed/personalized/', PersonalizedFeedView.as_view(), name='personalized-feed'),
    
    # Alternative feed access through posts endpoint
    path('posts/feed/', PostViewSet.as_view({'get': 'feed'}), name='posts-feed'),
    
    # Like/Unlike endpoints
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),
    path('posts/<int:post_id>/unlike/', UnlikePostView.as_view(), name='unlike-post'),
    path('posts/<int:post_id>/likes/', PostLikesListView.as_view(), name='post-likes-list'),
    path('comments/<int:comment_id>/like/', LikeCommentView.as_view(), name='like-comment'),
    path('comments/<int:comment_id>/unlike/', UnlikeCommentView.as_view(), name='unlike-comment'),
]