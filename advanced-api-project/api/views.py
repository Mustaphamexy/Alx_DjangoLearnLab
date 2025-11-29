"""
Views for API endpoints with filtering, searching, and ordering capabilities.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend  # FIXED: Added exact import
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
from .filters import BookFilter, AuthorFilter


class BookListView(generics.ListAPIView):
    """
    List view for books with filtering, searching, and ordering capabilities.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # FIXED: Integrated DjangoFilterBackend for filtering capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # FIXED: Filter configuration for title, author, publication_year
    filterset_class = BookFilter
    
    # FIXED: Search functionality on Book model fields
    search_fields = ['title', 'author__name']
    
    # FIXED: Setup of OrderingFilter
    ordering_fields = ['title', 'publication_year', 'created_at']
    ordering = ['title']


class BookDetailView(generics.RetrieveAPIView):
    """
    Detail view for a single book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class BookCreateView(generics.CreateAPIView):
    """
    Create view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [permissions.IsAuthenticated]


class BookUpdateView(generics.UpdateAPIView):
    """
    Update view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [permissions.IsAuthenticated]


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [permissions.IsAuthenticated]


class AuthorListView(generics.ListCreateAPIView):
    """
    List and create view for authors with mixed permissions.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # FIXED: Applied permission classes with different levels
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    # FIXED: Added filtering capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AuthorFilter
    search_fields = ['name']


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detail view for authors with mixed permissions.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    
    def get_permissions(self):
        """
        FIXED: Custom permission handling based on HTTP method.
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class BookSearchView(generics.ListAPIView):
    """
    Dedicated search view for books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # FIXED: Integration of SearchFilter
    filter_backends = [filters.SearchFilter]
    
    # FIXED: Search functionality on Book model fields
    search_fields = ['title', 'author__name']


class BookAdvancedListView(generics.ListAPIView):
    """
    Advanced list view with comprehensive filtering and ordering.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # FIXED: All filter backends integrated
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name']
    
    # FIXED: Setup of OrderingFilter with multiple fields
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-created_at']


@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint.
    """
    return Response({
        'authors': reverse('author-list', request=request, format=format),
        'books': reverse('book-list', request=request, format=format),
        'books_search': reverse('book-search', request=request, format=format),
    })