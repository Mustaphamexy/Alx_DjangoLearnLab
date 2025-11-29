"""
Data models for the Advanced API Project.

This module defines the Author and Book models which represent
the core data structure of our library API.
"""

from django.db import models

class Author(models.Model):
    """
    Author model representing a book author.
    
    Attributes:
        name (CharField): The name of the author (max 100 characters)
        created_at (DateTimeField): Auto-generated timestamp when author is created
        updated_at (DateTimeField): Auto-generated timestamp when author is updated
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Author model."""
        ordering = ['name']  # Default ordering by author name
    
    def __str__(self):
        """String representation of Author instance."""
        return self.name

class Book(models.Model):
    """
    Book model representing a published book.
    
    Attributes:
        title (CharField): The title of the book (max 200 characters)
        publication_year (IntegerField): The year the book was published
        author (ForeignKey): Reference to the Author who wrote the book
        created_at (DateTimeField): Auto-generated timestamp when book is created
        updated_at (DateTimeField): Auto-generated timestamp when book is updated
    
    Relationships:
        Each Author can have multiple Books (one-to-many relationship)
    """
    title = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    author = models.ForeignKey(
        Author, 
        on_delete=models.CASCADE,  # Delete books when author is deleted
        related_name='books'  # Enables author.books.all() to get all books by author
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Book model."""
        ordering = ['title']  # Default ordering by book title
        unique_together = ['title', 'author']  # Prevent duplicate books by same author
    
    def __str__(self):
        """String representation of Book instance."""
        return f"{self.title} by {self.author.name}"