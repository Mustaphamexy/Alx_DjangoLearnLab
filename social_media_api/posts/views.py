# posts/views.py

from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment
from .serializers import (
    PostSerializer, PostCreateSerializer,
    CommentSerializer, CommentCreateSerializer
)
from .permissions import IsOwnerOrReadOnly
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from .models import Like
from .serializers import LikeSerializer, LikeCreateSerializer
from notifications.models import Notification 



class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            liked = False
            message = 'Post unliked'
        else:
            post.likes.add(user)
            liked = True
            message = 'Post liked'
        
        return Response({
            'liked': liked,
            'like_count': post.like_count,
            'message': message
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            comment = serializer.save(author=request.user, post=post)
            return Response(CommentSerializer(comment, context={'request': request}).data,
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def feed(self, request):
        # Get posts from followed users
        following_users = request.user.following.all()
        posts = Post.objects.filter(author__in=following_users)
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def feed(self, request):
        """
        Get posts from users that the current user follows.
        Includes user's own posts and posts from followed users.
        """
        # Get users that the current user follows
        following_users = request.user.following.all()
        
        # Get the current user's ID
        current_user_id = request.user.id
        
        # Create a list of user IDs to include in the feed
        user_ids = [current_user_id]  # Include own posts
        user_ids.extend(following_users.values_list('id', flat=True))
        
        # Get posts from these users
        posts = Post.objects.filter(
            author_id__in=user_ids
        ).select_related('author').prefetch_related('comments', 'likes')
        
        # Apply pagination
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            comment = serializer.save(author=request.user, post=post)
            
            # Create notification for post author (if not commenting on own post)
            if post.author != request.user:
                from notifications.models import Notification
                Notification.create_comment_notification(
                    recipient=post.author,
                    actor=request.user,
                    target=post,
                    comment_text=comment.content
                )
            
            return Response(CommentSerializer(comment, context={'request': request}).data,
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            liked = False
            message = 'Comment unliked'
        else:
            comment.likes.add(user)
            liked = True
            message = 'Comment liked'
        
        return Response({
            'liked': liked,
            'like_count': comment.like_count,
            'message': message
        })

class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Enhanced feed view with filtering options
        """
        # Get following users
        following_users = request.user.following.all()
        
        # Create Q objects for the query
        queries = Q(author=request.user)  # Include own posts
        
        if following_users.exists():
            queries |= Q(author__in=following_users)
        
        # Get posts with optimizations
        posts = Post.objects.filter(queries).select_related('author').prefetch_related(
            'comments', 'likes', 'comments__author'
        ).order_by('-created_at')
        
        # Apply filters if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            posts = posts.filter(created_at__gte=start_date)
        if end_date:
            posts = posts.filter(created_at__lte=end_date)
        
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

class LikePostView(APIView):
    """View to like a post"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user already liked the post
        content_type = ContentType.objects.get_for_model(Post)
        like_exists = Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        ).exists()
        
        if like_exists:
            return Response(
                {'error': 'You have already liked this post'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the like
        like = Like.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        )
        
        # Create notification for post author (if not liking own post)
        if post.author != request.user:
            Notification.create_like_notification(
                recipient=post.author,
                actor=request.user,
                target=post
            )
        
        return Response({
            'message': 'Post liked successfully',
            'like_id': like.id,
            'like_count': post.like_count
        }, status=status.HTTP_201_CREATED)

class UnlikePostView(APIView):
    """View to unlike a post"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove the like
        content_type = ContentType.objects.get_for_model(Post)
        Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        ).delete()
        
        return Response({
            'message': 'Post unliked successfully',
            'like_count': post.like_count
        }, status=status.HTTP_200_OK)

class LikeCommentView(APIView):
    """View to like a comment"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user already liked the comment
        content_type = ContentType.objects.get_for_model(Comment)
        like_exists = Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=comment.id
        ).exists()
        
        if like_exists:
            return Response(
                {'error': 'You have already liked this comment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the like
        like = Like.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=comment.id
        )
        
        # Create notification for comment author (if not liking own comment)
        if comment.author != request.user:
            Notification.create_like_notification(
                recipient=comment.author,
                actor=request.user,
                target=comment
            )
        
        return Response({
            'message': 'Comment liked successfully',
            'like_id': like.id,
            'like_count': comment.like_count
        }, status=status.HTTP_201_CREATED)

class UnlikeCommentView(APIView):
    """View to unlike a comment"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove the like
        content_type = ContentType.objects.get_for_model(Comment)
        Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=comment.id
        ).delete()
        
        return Response({
            'message': 'Comment unliked successfully',
            'like_count': comment.like_count
        }, status=status.HTTP_200_OK)

class PostLikesListView(generics.ListAPIView):
    """View to list all users who liked a post"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = LikeSerializer
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        content_type = ContentType.objects.get_for_model(Post)
        return Like.objects.filter(
            content_type=content_type,
            object_id=post_id
        ).select_related('user')


class PersonalizedFeedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        feed_type = request.query_params.get('type', 'personalized')
        
        if feed_type == 'trending':
            # Import the FeedAlgorithm class
            from .feed_algorithm import FeedAlgorithm
            posts = FeedAlgorithm.get_trending_posts(request.user)
        else:
            from .feed_algorithm import FeedAlgorithm
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