# Django Admin Configuration for Book Model

## 1. Admin Registration

**File:** `bookshelf/admin.py`

```python
from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = ['title', 'author', 'publication_year']
    
    # Add filters for author and publication year
    list_filter = ['author', 'publication_year']
    
    # Enable search by title and author
    search_fields = ['title', 'author']
    
    # Allow editing author and publication year directly from list
    list_editable = ['author', 'publication_year']
    
    # Pagination
    list_per_page = 20
    
    # Default ordering
    ordering = ['title']