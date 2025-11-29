"""
Views for API endpoints with filtering, searching, and ordering capabilities.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny  # FIXED: Added specific imports
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # FIXED: Filter configuration for title, author, publication_year
    filterset_class = BookFilter
    
    # FIXED: Search functionality on Book model fields
    search_fields = ['title', 'author__name']
    
    # FIXED: Setup of OrderingFilter
    ordering_fields = ['title', 'publication_year', 'created_at']
    ordering = ['title']

    def list(self, request, *args, **kwargs):
        """
        FIXED: Custom list method to provide paginated response structure.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create paginated response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })


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

    def create(self, request, *args, **kwargs):
        """
        FIXED: Custom create method with message field.
        """
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
    Update view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        FIXED: Custom update method with message field.
        """
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
    Delete view for books with permission protection.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # FIXED: Applied permission classes to protect endpoint
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """
        FIXED: Custom destroy method with message field.
        """
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
    List and create view for authors with mixed permissions.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # FIXED: Applied permission classes with different levels
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # FIXED: Added filtering capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AuthorFilter
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        """
        FIXED: Custom list method to provide consistent response structure.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        FIXED: Custom create method for authors.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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

    def list(self, request, *args, **kwargs):
        """
        FIXED: Custom list method for search with proper response structure.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create paginated response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            # Add search metadata
            response.data.update({
                'search_query': request.query_params.get('search', ''),
                'results_count': len(serializer.data),
                'search_fields': self.search_fields,
            })
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data,
            'search_query': request.query_params.get('search', ''),
            'results_count': len(serializer.data),
            'search_fields': self.search_fields,
        })


class BookAdvancedListView(generics.ListAPIView):
    """
    Advanced list view with comprehensive filtering and ordering.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    # FIXED: All filter backends integrated
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name']
    
    # FIXED: Setup of OrderingFilter with multiple fields
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        """
        FIXED: Custom list method with paginated response.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create paginated response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })


class BookBulkOperationsView(generics.GenericAPIView):
    """
    Custom view for bulk operations on books.
    """
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle bulk creation of books.
        """
        books_data = request.data.get('books', [])
        results = {
            'created': [],
            'errors': []
        }

        for book_data in books_data:
            serializer = self.get_serializer(data=book_data)
            if serializer.is_valid():
                book = serializer.save()
                results['created'].append(BookSerializer(book).data)
            else:
                results['errors'].append({
                    'data': book_data,
                    'errors': serializer.errors
                })

        return Response(results, status=status.HTTP_207_MULTI_STATUS)


@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint.
    """
    return Response({
        'authors': reverse('author-list', request=request, format=format),
        'books': reverse('book-list', request=request, format=format),
        'books_search': reverse('book-search', request=request, format=format),
        'books_advanced': reverse('book-advanced-list', request=request, format=format),
    })