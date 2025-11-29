"""
Custom filter classes for the Advanced API Project.

This module defines custom filters for Book model with advanced filtering
capabilities including exact matches, range filters, and custom lookups.
"""

import django_filters
from django_filters import rest_framework as filters
from django.db import models
from .models import Book, Author


class BookFilter(filters.FilterSet):
    """
    Custom FilterSet for Book model providing advanced filtering options.
    
    Features:
    - Exact matching on title, author, and publication_year
    - Range filtering for publication_year
    - Case-insensitive title search
    - Multiple field lookups for flexible querying
    """
    
    # Exact match filters
    title = django_filters.CharFilter(
        field_name='title', 
        lookup_expr='exact',
        help_text="Exact match for book title"
    )
    
    title_icontains = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text="Case-insensitive partial match for book title"
    )
    
    author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.all(),
        help_text="Filter by specific author ID"
    )
    
    author_name = django_filters.CharFilter(
        field_name='author__name',
        lookup_expr='icontains',
        help_text="Case-insensitive partial match for author name"
    )
    
    publication_year = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='exact',
        help_text="Exact match for publication year"
    )
    
    # Range filters
    publication_year_min = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='gte',
        help_text="Books published in or after this year"
    )
    
    publication_year_max = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='lte',
        help_text="Books published in or before this year"
    )
    
    # Date range filters for created_at
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Books created after this date/time"
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Books created before this date/time"
    )

    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains'],
            'author': ['exact'],
            'publication_year': ['exact', 'gte', 'lte'],
        }
    
    @property
    def qs(self):
        """
        Custom queryset method to add additional filtering logic.
        
        Returns:
            QuerySet: Filtered book queryset with additional optimizations
        """
        queryset = super().qs
        # Additional custom filtering logic can be added here
        return queryset.select_related('author')


class AuthorFilter(filters.FilterSet):
    """
    FilterSet for Author model with book count filtering.
    """
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text="Case-insensitive partial match for author name"
    )
    
    has_books = django_filters.BooleanFilter(
        method='filter_has_books',
        help_text="Filter authors who have books (true) or no books (false)"
    )
    
    min_books = django_filters.NumberFilter(
        method='filter_min_books',
        help_text="Authors with at least this many books"
    )
    
    max_books = django_filters.NumberFilter(
        method='filter_max_books',
        help_text="Authors with at most this many books"
    )

    class Meta:
        model = Author
        fields = ['name']

    def filter_has_books(self, queryset, name, value):
        """
        Custom method to filter authors based on whether they have books.
        """
        if value:
            return queryset.filter(books__isnull=False).distinct()
        else:
            return queryset.filter(books__isnull=True)
    
    def filter_min_books(self, queryset, name, value):
        """
        Custom method to filter authors with minimum number of books.
        """
        return queryset.annotate(book_count=models.Count('books')).filter(book_count__gte=value)
    
    def filter_max_books(self, queryset, name, value):
        """
        Custom method to filter authors with maximum number of books.
        """
        return queryset.annotate(book_count=models.Count('books')).filter(book_count__lte=value)