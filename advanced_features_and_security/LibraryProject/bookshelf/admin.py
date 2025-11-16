from django.contrib import admin
from .models import Book, Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']  # Remove 'publication_year'
    list_filter = ['author']  # Remove 'publication_year'
    search_fields = ['title', 'author__name']  # Fixed: use 'author__name' not 'author'
    # Remove list_editable since it references non-existent field
    list_per_page = 20
    ordering = ['title']