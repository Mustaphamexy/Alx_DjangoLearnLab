# accounts/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from .models import CustomUser
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializers import FollowSerializer, FollowUserSerializer, FollowListSerializer
from notifications.models import Notification

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the token to logout
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        logout(request)
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            
            # Prevent following yourself
            if user_id == request.user.id:
                return Response(
                    {'error': 'You cannot follow yourself.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the user to follow
            user_to_follow = get_object_or_404(CustomUser, id=user_id)
            
            # Check if already following
            if request.user.is_following(user_to_follow):
                return Response(
                    {'error': 'You are already following this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add to following
            request.user.following.add(user_to_follow)
            
            # Create notification for the followed user
            from notifications.models import Notification
            Notification.create_follow_notification(
                recipient=user_to_follow,
                actor=request.user
            )
            
            return Response({
                'message': f'You are now following {user_to_follow.username}',
                'following': True,
                'followers_count': user_to_follow.follower_count,
                'following_count': request.user.following_count
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            
            # Prevent unfollowing yourself
            if user_id == request.user.id:
                return Response(
                    {'error': 'You cannot unfollow yourself.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the user to unfollow
            user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
            
            # Check if actually following
            if not request.user.is_following(user_to_unfollow):
                return Response(
                    {'error': 'You are not following this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Remove from following
            request.user.following.remove(user_to_unfollow)
            
            # No need to delete notification as it's a historical record
            
            return Response({
                'message': f'You have unfollowed {user_to_unfollow.username}',
                'following': False,
                'followers_count': user_to_unfollow.follower_count,
                'following_count': request.user.following_count
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FollowersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowListSerializer
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        return user.followers.all()

class FollowingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowListSerializer
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        return user.following.all()

class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUserSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return CustomUser.objects.filter(
                username__icontains=query
            ).exclude(id=self.request.user.id)[:10]
        return CustomUser.objects.none()