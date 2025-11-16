from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'relationship_app'

urlpatterns = [
    # Public pages
    path('', views.home_view, name='home'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Role-based dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('librarian/dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('member/dashboard/', views.member_dashboard, name='member_dashboard'),
    
    # Book views
    path('books/', views.list_books, name='list_books'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('books/management/', views.book_management, name='book_management'),
    
    # Author views
    path('authors/add/', views.add_author, name='add_author'),
    
    # Library views
    path('libraries/', views.LibraryListView.as_view(), name='library_list'),
    path('libraries/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),
    path('libraries/add/', views.add_library, name='add_library'),
    path('libraries/<int:pk>/edit/', views.edit_library, name='edit_library'),
    path('libraries/<int:pk>/delete/', views.delete_library, name='delete_library'),
    
    # Management views
    path('admin/manage-roles/', views.manage_roles, name='manage_roles'),
    path('admin/user-management/', views.user_management, name='user_management'),
    
    # API endpoints
    path('api/user-stats/', views.get_user_stats, name='user_stats'),
    
    # Password reset (using Django's built-in views)
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='relationship_app/password_change.html',
        success_url='/relationship/dashboard/'
    ), name='password_change'),
]