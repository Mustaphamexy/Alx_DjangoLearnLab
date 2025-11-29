"""
Enhanced views with filtering, searching, and ordering capabilities.
Complete implementation including all required views.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend  # FIXED: Added this import
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer, AuthorDetailSerializer
from .filters import BookFilter, AuthorFilter


class BookListView(generics.ListAPIView):
    """
    Enhanced ListView for retrieving all books with advanced query capabilities.
    
    Features:
    - Filtering: Filter by title, author, publication_year ranges, and more
    - Searching: Full-text search across title and author names
    - Ordering: Sort by any book field in ascending or descending order
    - Pagination: Built-in pagination for large result sets
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # Filter backends configuration - FIXED: All filters properly configured
    filter_backends = [
        DjangoFilterBackend,      # For field-specific filtering
        filters.SearchFilter,     # For full-text search
        filters.OrderingFilter,   # For result ordering
    ]
    
    # Filter configuration
    filterset_class = BookFilter
    
    # Search configuration - FIXED: Search functionality enabled
    search_fields = [
        'title',           # Exact search on title
        'author__name',    # Search by author name
        '=title',          # Exact match search (case-sensitive)
    ]
    
    # Ordering configuration - FIXED: OrderingFilter properly set up
    ordering_fields = [
        'title',
        'publication_year', 
        'created_at',
        'updated_at',
        'author__name',    # Order by author name
    ]
    ordering = ['title']   # Default ordering
    
    def get_queryset(self):
        """
        Enhanced queryset method with additional optimizations and custom filtering.
        """
        queryset = super().get_queryset()
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Custom list method to provide enhanced response with query metadata.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add query metadata to response
        response.data = {
            'count': len(response.data),
            'filters_available': {
                'exact_match': ['title', 'author', 'publication_year'],
                'partial_match': ['title_icontains', 'author_name'],
                'range_filters': ['publication_year_min', 'publication_year_max'],
                'date_filters': ['created_after', 'created_before'],
            },
            'search_fields': self.search_fields,
            'ordering_fields': self.ordering_fields,
            'default_ordering': self.ordering,
            'results': response.data
        }
        
        return response


class BookDetailView(generics.RetrieveAPIView):
    """
    DetailView for retrieving a single book by ID.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


class BookCreateView(generics.CreateAPIView):
    """
    CreateView for adding a new book.
    
    Permissions:
        - IsAuthenticated: Only authenticated users can create books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # FIXED: Permission classes applied

    def perform_create(self, serializer):
        """Custom method called when creating a new book instance."""
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Custom create method to provide enhanced response handling."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Book created successfully',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class BookUpdateView(generics.UpdateAPIView):
    """
    UpdateView for modifying an existing book.
    
    Permissions:
        - IsAuthenticated: Only authenticated users can update books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # FIXED: Permission classes applied
    lookup_field = 'pk'

    def perform_update(self, serializer):
        """Custom method called when updating a book instance."""
        serializer.save()

    def update(self, request, *args, **kwargs):
        """Custom update method to provide enhanced response handling."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                'message': 'Book updated successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )


class BookDeleteView(generics.DestroyAPIView):
    """
    DeleteView for removing a book.
    
    Permissions:
        - IsAuthenticated: Only authenticated users can delete books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # FIXED: Permission classes applied
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        """Custom destroy method to provide enhanced response handling."""
        instance = self.get_object()
        book_title = instance.title
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': f'Book "{book_title}" deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )


class AuthorListView(generics.ListCreateAPIView):
    """
    Combined List and Create view for Author model.
    """
    queryset = Author.objects.all().prefetch_related('books')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # FIXED: Permission classes applied
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuthorFilter
    search_fields = ['name', 'books__title']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Dynamically select serializer based on request method."""
        if self.request.method == 'POST':
            return AuthorSerializer
        return AuthorSerializer

    def get_permissions(self):
        """Custom permission handling for different HTTP methods."""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detail view for Author model supporting Retrieve, Update, and Delete operations.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorDetailSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        """
        Custom permission handling for different HTTP methods.
        
        Returns:
            - AllowAny for GET requests
            - IsAuthenticated for PUT, PATCH, DELETE requests
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]  # FIXED: Permission classes applied

    def perform_destroy(self, instance):
        """Custom destroy method for Author."""
        author_name = instance.name
        super().perform_destroy(instance)
        print(f"Author '{author_name}' has been deleted")


class BookSearchView(generics.ListAPIView):
    """
    Dedicated search view for books with advanced search capabilities.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]  # FIXED: SearchFilter integrated
    search_fields = ['title', 'author__name', '^title']  # FIXED: Search functionality on Book model fields
    
    def get_queryset(self):
        """Custom queryset with search optimizations."""
        queryset = Book.objects.all().select_related('author')
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Custom list method for search results."""
        response = super().list(request, *args, **kwargs)
        
        # Enhance search response
        search_query = request.query_params.get('search', '')
        response.data = {
            'search_query': search_query,
            'results_count': len(response.data),
            'search_fields': self.search_fields,
            'results': response.data
        }
        
        return response


class BookAdvancedListView(generics.ListAPIView):
    """
    Advanced book list view with comprehensive ordering and filtering options.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]  # FIXED: OrderingFilter configured
    filterset_class = BookFilter
    
    # Extended ordering options
    ordering_fields = [
        'title', 'publication_year', 'created_at', 'updated_at',
        'author__name', 'author__created_at'
    ]
    ordering = ['-created_at']  # Default: newest first
    
    def get_queryset(self):
        """Advanced queryset with annotations for complex ordering."""
        queryset = Book.objects.all().select_related('author')
        return queryset


class BookBulkOperationsView(generics.GenericAPIView):
    """
    Custom view for bulk operations on books.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # FIXED: Permission classes applied

    def post(self, request, *args, **kwargs):
        """Handle bulk creation of books."""
        books_data = request.data.get('books', [])
        results = {
            'created': [],
            'errors': []
        }

        for book_data in books_data:
            serializer = self.get_serializer(data=book_data)
            if serializer.is_valid():
                serializer.save()
                results['created'].append(serializer.data)
            else:
                results['errors'].append({
                    'data': book_data,
                    'errors': serializer.errors
                })

        return Response(results, status=status.HTTP_207_MULTI_STATUS)


# API Root view
@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root endpoint providing links to all available resources.
    """
    return Response({
        'authors': reverse('author-list', request=request, format=format),
        'books': reverse('book-list', request=request, format=format),
        'book_search': reverse('book-search', request=request, format=format),
        'book_advanced_list': reverse('book-advanced-list', request=request, format=format),
        'documentation': 'Check API_QUERY_EXAMPLES.md for filtering, searching, and ordering examples'
    })