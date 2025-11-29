"""
Comprehensive tests for filtering, searching, and ordering functionality.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author, Book


class FilterSearchOrderTests(APITestCase):
    """
    Test filtering, searching, and ordering capabilities.
    """
    
    def setUp(self):
        """
        Set up test data with varied books and authors.
        """
        # Create authors
        self.author1 = Author.objects.create(name='J.K. Rowling')
        self.author2 = Author.objects.create(name='George Orwell')
        self.author3 = Author.objects.create(name='J.R.R. Tolkien')
        
        # Create books with varied data
        self.books = [
            Book.objects.create(
                title='Harry Potter',
                publication_year=1997,
                author=self.author1
            ),
            Book.objects.create(
                title='1984',
                publication_year=1949,
                author=self.author2
            ),
            Book.objects.create(
                title='Animal Farm',
                publication_year=1945,
                author=self.author2
            ),
            Book.objects.create(
                title='The Hobbit',
                publication_year=1937,
                author=self.author3
            ),
            Book.objects.create(
                title='Harry Potter and the Chamber of Secrets',
                publication_year=1998,
                author=self.author1
            ),
        ]
        
        self.book_list_url = reverse('book-list')

    def test_filter_by_author(self):
        """
        Test filtering books by specific author.
        """
        response = self.client.get(self.book_list_url, {'author': self.author1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # J.K. Rowling has 2 books
        self.assertEqual(response.data['results'][0]['author'], self.author1.id)

    def test_filter_by_publication_year_range(self):
        """
        Test filtering books by publication year range.
        """
        response = self.client.get(
            self.book_list_url, 
            {
                'publication_year_min': 1950,
                'publication_year_max': 2000
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return Harry Potter books (1997, 1998)
        self.assertEqual(response.data['count'], 2)

    def test_search_functionality(self):
        """
        Test full-text search across title and author names.
        """
        # Search for "Harry"
        response = self.client.get(self.book_list_url, {'search': 'Harry'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Search for author name
        response = self.client.get(self.book_list_url, {'search': 'Orwell'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # 1984 and Animal Farm

    def test_ordering_ascending(self):
        """
        Test ascending ordering by publication year.
        """
        response = self.client.get(self.book_list_url, {'ordering': 'publication_year'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        
        # Check that books are ordered by publication year ascending
        years = [book['publication_year'] for book in results]
        self.assertEqual(years, sorted(years))

    def test_ordering_descending(self):
        """
        Test descending ordering by title.
        """
        response = self.client.get(self.book_list_url, {'ordering': '-title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        
        # Check that books are ordered by title descending
        titles = [book['title'] for book in results]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_combined_filter_search_order(self):
        """
        Test combining filtering, searching, and ordering.
        """
        response = self.client.get(
            self.book_list_url,
            {
                'author_name': 'Rowling',  # Filter
                'ordering': '-publication_year',  # Order
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Check ordering (should be newest first)
        results = response.data['results']
        self.assertEqual(results[0]['publication_year'], 1998)  # Chamber of Secrets
        self.assertEqual(results[1]['publication_year'], 1997)  # Harry Potter

    def test_title_icontains_filter(self):
        """
        Test case-insensitive partial title matching.
        """
        response = self.client.get(self.book_list_url, {'title_icontains': 'harry'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_exact_title_filter(self):
        """
        Test exact title matching.
        """
        response = self.client.get(self.book_list_url, {'title': '1984'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], '1984')

    def test_author_advanced_filter(self):
        """
        Test advanced author filtering options.
        """
        # Test author with books
        author_list_url = reverse('author-list')
        response = self.client.get(author_list_url, {'has_books': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # All authors have books


class SearchViewTests(APITestCase):
    """
    Test dedicated search view functionality.
    """
    
    def setUp(self):
        self.author = Author.objects.create(name='Test Author')
        Book.objects.create(title='Python Programming', publication_year=2020, author=self.author)
        Book.objects.create(title='Advanced Python', publication_year=2021, author=self.author)
        
        self.search_url = reverse('book-search')

    def test_dedicated_search(self):
        """
        Test dedicated search view.
        """
        response = self.client.get(self.search_url, {'search': 'Python'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results_count'], 2)
        self.assertEqual(response.data['search_query'], 'Python')