# accounts/urls.py

from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserProfileView, UserProfileDetailView,
    FollowUserView, UnfollowUserView,  # New imports
    FollowersListView, FollowingListView, UserSearchView
)

urlpatterns = [
    # ... existing auth URLs ...
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', UserProfileDetailView.as_view(), name='profile-detail'),
    
    # Follow/Unfollow endpoints
    path('follow/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/', UnfollowUserView.as_view(), name='unfollow-user'),
    
    # Followers/Following lists
    path('users/<int:user_id>/followers/', FollowersListView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', FollowingListView.as_view(), name='user-following'),
    
    # User search
    path('users/search/', UserSearchView.as_view(), name='user-search'),
]