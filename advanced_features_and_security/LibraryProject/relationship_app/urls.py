from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'relationship_app'

urlpatterns = [
    # Book and Library URLs
    path('books/', views.list_books, name='list_books'),
    path('libraries/', views.LibraryListView.as_view(), name='library_list'),
    path('libraries/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),
    
    # Library Management URLs with Permissions
    path('libraries/add/', views.add_library, name='add_library'),
    path('libraries/<int:pk>/edit/', views.edit_library, name='edit_library'),
    path('libraries/<int:pk>/delete/', views.delete_library, name='delete_library'),
    
    # Authentication URLs (using our custom views)
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Role-Based URLs
    path('admin/', views.admin_view, name='admin_view'),
    path('librarian/', views.librarian_view, name='librarian_view'),
    path('member/', views.member_view, name='member_view'),
    path('manage-roles/', views.manage_roles, name='manage_roles'),
    
    # Book Management URLs with Permissions
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('books/management/', views.book_management, name='book_management'),
]