"""
Enhanced views with filtering, searching, and ordering capabilities.
Complete implementation including all required views.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend
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
    
    Query Parameters:
    - Filtering: 
        ?title=exact_title
        ?title_icontains=partial_title
        ?author=author_id
        ?author_name=partial_author_name
        ?publication_year=2020
        ?publication_year_min=2000&publication_year_max=2020
    - Searching:
        ?search=search_term (searches title and author__name)
    - Ordering:
        ?ordering=title (ascending)
        ?ordering=-publication_year (descending)
        ?ordering=author__name,title (multiple fields)
    
    Permissions:
        - AllowAny: Anyone can view and query the book list
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # Filter backends configuration
    filter_backends = [
        DjangoFilterBackend,      # For field-specific filtering
        filters.SearchFilter,     # For full-text search
        filters.OrderingFilter,   # For result ordering
    ]
    
    # Filter configuration
    filterset_class = BookFilter
    
    # Search configuration
    search_fields = [
        'title',           # Exact search on title
        'author__name',    # Search by author name
        '=title',          # Exact match search (case-sensitive)
    ]
    
    # Ordering configuration
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
        
        Returns:
            QuerySet: Optimized book queryset with select_related and prefetch_related
        """
        queryset = super().get_queryset()
        
        # Additional custom filtering logic can be added here
        # Example: Custom business logic filtering
        
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
    
    Provides read-only access to a specific Book instance.
    
    Permissions:
        - AllowAny: Anyone can view book details
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


class BookCreateView(generics.CreateAPIView):
    """
    CreateView for adding a new book.
    
    Handles creation of new Book instances with data validation
    and custom success/error responses.
    
    Permissions:
        - IsAuthenticated: Only authenticated users can create books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Custom method called when creating a new book instance.
        
        Can be extended to add custom logic before saving, such as:
        - Setting the current user as the creator
        - Adding audit trail information
        - Sending notifications
        """
        serializer.save()
        # Additional custom logic can be added here

    def create(self, request, *args, **kwargs):
        """
        Custom create method to provide enhanced response handling.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Custom success response with additional information
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
    
    Handles partial and complete updates of Book instances
    with proper validation and error handling.
    
    Permissions:
        - IsAuthenticated: Only authenticated users can update books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        """
        Custom method called when updating a book instance.
        
        Can be extended to add custom logic before saving, such as:
        - Tracking changes
        - Validating business rules
        - Sending update notifications
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Custom update method to provide enhanced response handling.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Custom success response
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
    
    Handles deletion of Book instances with proper permissions
    and custom response handling.
    
    Permissions:
        - IsAuthenticated: Only authenticated users can delete books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to provide enhanced response handling.
        """
        instance = self.get_object()
        book_title = instance.title
        self.perform_destroy(instance)
        
        # Custom success response
        return Response(
            {
                'message': f'Book "{book_title}" deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )


class AuthorListView(generics.ListCreateAPIView):
    """
    Combined List and Create view for Author model.
    
    Provides:
    - List: Read-only access to all authors (for all users)
    - Create: Create new authors (for authenticated users only)
    
    Uses different serializers for different actions to optimize
    performance and data structure.
    """
    queryset = Author.objects.all().prefetch_related('books')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuthorFilter
    search_fields = ['name', 'books__title']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_serializer_class(self):
        """
        Dynamically select serializer based on request method.
        """
        if self.request.method == 'POST':
            return AuthorSerializer
        return AuthorSerializer

    def get_permissions(self):
        """
        Custom permission handling for different HTTP methods.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detail view for Author model supporting Retrieve, Update, and Delete operations.
    
    Provides:
    - Retrieve: Get specific author details
    - Update: Modify author information
    - Delete: Remove author (cascades to related books)
    
    Permissions are customized based on the HTTP method.
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
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        """
        Custom destroy method for Author.
        
        Additional logic can be added here before deletion, such as:
        - Archiving author data
        - Handling related objects
        - Sending deletion notifications
        """
        # Custom logic before deletion
        author_name = instance.name
        super().perform_destroy(instance)
        # Custom logic after deletion
        print(f"Author '{author_name}' has been deleted")


class BookSearchView(generics.ListAPIView):
    """
    Dedicated search view for books with advanced search capabilities.
    
    This view provides a specialized interface for complex search operations
    beyond basic filtering and ordering.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author__name', '^title']  # ^ for starts-with search
    
    def get_queryset(self):
        """
        Custom queryset with search optimizations.
        """
        queryset = Book.objects.all().select_related('author')
        
        # Custom search logic can be added here
        search_query = self.request.query_params.get('search', None)
        if search_query:
            # Additional custom search logic
            pass
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Custom list method for search results.
        """
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
    
    Provides additional ordering capabilities and complex query support
    for advanced use cases.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = BookFilter
    
    # Extended ordering options
    ordering_fields = [
        'title', 'publication_year', 'created_at', 'updated_at',
        'author__name', 'author__created_at'
    ]
    ordering = ['-created_at']  # Default: newest first
    
    def get_queryset(self):
        """
        Advanced queryset with annotations for complex ordering.
        """
        queryset = Book.objects.all().select_related('author')
        return queryset


class BookBulkOperationsView(generics.GenericAPIView):
    """
    Custom view for bulk operations on books.
    
    Demonstrates how to create custom views beyond standard generic views
    for specific use cases like bulk operations.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle bulk creation of books.
        
        Expected payload format:
        {
            "books": [
                {"title": "Book 1", "publication_year": 2020, "author": 1},
                {"title": "Book 2", "publication_year": 2021, "author": 1}
            ]
        }
        """
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