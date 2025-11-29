from django.contrib import admin
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publication_year', 'created_at']
    list_filter = ['author', 'publication_year']
    search_fields = ['title', 'author__name']