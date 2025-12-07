from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),
    
    # Posts
    path('posts/', views.PostListView.as_view(), name='post-list'),
    path('posts/create/', views.PostCreateView.as_view(), name='post-create'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<slug:slug>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('posts/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    
    # Comments
    path('comments/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment-update'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('posts/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='comment-create'),
    
    # Search
    path('search/', views.search_posts, name='search-posts'),
    
    # Categories
    path('category/<slug:slug>/', views.CategoryPostListView.as_view(), name='category-posts'),
    
    # Tags
    path('tags/', views.tag_cloud, name='tag-cloud'),
    path('tag/<slug:slug>/', views.TagPostListView.as_view(), name='tag-posts'),
    
    # User
    path('my-posts/', views.UserPostListView.as_view(), name='user-posts'),
    path('profile/', views.profile, name='profile'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # Password reset (simplified - using default Django templates)
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)