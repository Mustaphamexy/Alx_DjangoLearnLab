"""
Views for API endpoints with filtering, searching, and ordering capabilities.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django_filters import rest_framework  # FIXED: Added exact import
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
from .filters import BookFilter, AuthorFilter


class BookListView(generics.ListAPIView):
    """
    List view for books with filtering, searching, and ordering capabilities.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    # FIXED: Integrated DjangoFilterBackend for filtering capabilities
    filter_backends = [rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
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
    permission_classes = [AllowAny]


class BookCreateView(generics.CreateAPIView):
    """
    Create view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [IsAuthenticated]


class BookUpdateView(generics.UpdateAPIView):
    """
    Update view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [IsAuthenticated]


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [IsAuthenticated]


class AuthorListView(generics.ListCreateAPIView):
    """
    List and create view for authors with mixed permissions.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # FIXED: Applied permission classes with different levels
    permission_classes = [IsAuthenticatedOrReadOnly]


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
            return [AllowAny()]
        return [IsAuthenticated()]


class BookSearchView(generics.ListAPIView):
    """
    Dedicated search view for books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]
    
    # FIXED: All filter backends integrated
    filter_backends = [rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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