# posts/feed_algorithm.py

from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Post
from .serializers import PostSerializer

class FeedAlgorithm:
    @staticmethod
    def get_personalized_feed(user, limit=50):
        """
        Get personalized feed based on user's interactions
        """
        # Get users the current user follows
        following_users = user.following.all()
        
        # Start with posts from followed users
        posts = Post.objects.filter(
            Q(author__in=following_users) | Q(author=user)
        )
        
        # Boost posts with recent interactions
        recent_posts = posts.annotate(
            recent_likes=Count('likes', filter=Q(
                likes__liked_posts__created_at__gte=timezone.now() - timedelta(days=7)
            )),
            recent_comments=Count('comments', filter=Q(
                comments__created_at__gte=timezone.now() - timedelta(days=7)
            ))
        ).order_by(
            '-recent_likes',
            '-recent_comments',
            '-created_at'
        )[:limit]
        
        return recent_posts
    
    @staticmethod
    def get_trending_posts(user, days=7, limit=20):
        """
        Get trending posts (not necessarily from followed users)
        """
        trending_posts = Post.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=days)
        ).annotate(
            total_likes=Count('likes'),
            total_comments=Count('comments')
        ).order_by(
            '-total_likes',
            '-total_comments',
            '-created_at'
        )[:limit]
        
        return trending_posts

# Update the FeedView to use the algorithm
class PersonalizedFeedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        feed_type = request.query_params.get('type', 'personalized')
        
        if feed_type == 'trending':
            posts = FeedAlgorithm.get_trending_posts(request.user)
        else:
            posts = FeedAlgorithm.get_personalized_feed(request.user)
        
        # Paginate results
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(
            result_page,
            many=True,
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)