"""
URL configuration for api app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Author endpoints
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    
    # Book endpoints
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('books/bulk/', views.BookBulkOperationsView.as_view(), name='book-bulk'),  # FIXED: Added bulk endpoint
    
    # Search and advanced endpoints
    path('books/search/', views.BookSearchView.as_view(), name='book-search'),
    path('books/advanced/', views.BookAdvancedListView.as_view(), name='book-advanced-list'),
    
    # API root
    path('', views.api_root, name='api-root'),
]