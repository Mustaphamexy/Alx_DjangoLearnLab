"""
Custom serializers for the Advanced API Project.

This module defines serializers that handle complex data structures,
nested relationships, and custom validation for the Author and Book models.
"""

from rest_framework import serializers
from .models import Author, Book
from datetime import datetime

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model with custom validation.
    
    Handles serialization/deserialization of Book instances and includes
    custom validation for publication_year to ensure it's not in the future.
    
    Fields:
        id (Integer): Primary key (read-only)
        title (String): Book title
        publication_year (Integer): Year of publication with custom validation
        author (PrimaryKeyRelatedField): Reference to Author ID
        created_at (DateTime): Creation timestamp (read-only)
        updated_at (DateTime): Last update timestamp (read-only)
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_publication_year(self, value):
        """
        Custom validation for publication_year field.
        
        Ensures that the publication year is not in the future.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: The validated publication year
            
        Raises:
            serializers.ValidationError: If publication year is in the future
        """
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value

class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for Author model with nested BookSerializer.
    
    Handles serialization/deserialization of Author instances and includes
    a nested representation of related books using BookSerializer.
    
    Fields:
        id (Integer): Primary key (read-only)
        name (String): Author name
        books (Nested BookSerializer): List of books by this author (read-only)
        created_at (DateTime): Creation timestamp (read-only)
        updated_at (DateTime): Last update timestamp (read-only)
    """
    
    # Nested serializer for related books
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AuthorDetailSerializer(AuthorSerializer):
    """
    Detailed Author serializer with additional book information.
    
    Extends AuthorSerializer to provide more detailed book information
    when retrieving individual author instances.
    """
    pass