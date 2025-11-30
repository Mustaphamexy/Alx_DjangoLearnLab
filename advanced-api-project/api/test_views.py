"""
Unit tests for API endpoints.
Testing API endpoints for functionality, response data integrity, and status code accuracy.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Author, Book


class BaseAPITestCase(APITestCase):
    """
    Base test case that uses separate test database.
    Django automatically configures test database to avoid impacting production.
    """
    
    def setUp(self):
        """
        Set up test data using separate test database.
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test author
        self.author = Author.objects.create(name='Test Author')
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            publication_year=2020,
            author=self.author
        )
        
        # Create API client
        self.client = APIClient()


class BookCRUDTests(BaseAPITestCase):
    """
    Test Book CRUD operations and status codes.
    """
    
    def test_book_list_returns_correct_status(self):
        """
        Test book list returns correct status code.
        """
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_detail_returns_correct_status(self):
        """
        Test book detail returns correct status code.
        """
        response = self.client.get(reverse('book-detail', kwargs={'pk': self.book.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_create_without_auth_returns_403(self):
        """
        Test book creation without authentication returns 403.
        """
        book_data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author.pk
        }
        response = self.client.post(reverse('book-create'), book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_book_create_with_auth_returns_201(self):
        """
        Test book creation with authentication returns 201.
        """
        # FIXED: Added self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        book_data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author.pk
        }
        response = self.client.post(reverse('book-create'), book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_book_update_without_auth_returns_403(self):
        """
        Test book update without authentication returns 403.
        """
        update_data = {'title': 'Updated Book'}
        response = self.client.put(
            reverse('book-update', kwargs={'pk': self.book.pk}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_book_update_with_auth_returns_200(self):
        """
        Test book update with authentication returns 200.
        """
        # FIXED: Added self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        update_data = {
            'title': 'Updated Book',
            'publication_year': 2021,
            'author': self.author.pk
        }
        response = self.client.put(
            reverse('book-update', kwargs={'pk': self.book.pk}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_delete_without_auth_returns_403(self):
        """
        Test book delete without authentication returns 403.
        """
        response = self.client.delete(reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_book_delete_with_auth_returns_204(self):
        """
        Test book delete with authentication returns 204.
        """
        # FIXED: Added self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        response = self.client.delete(reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AuthorPermissionTests(BaseAPITestCase):
    """
    Test author endpoint permissions and status codes.
    """
    
    def test_author_list_returns_200(self):
        """
        Test author list returns 200 for unauthenticated users.
        """
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_author_create_without_auth_returns_403(self):
        """
        Test author creation without authentication returns 403.
        """
        author_data = {'name': 'New Author'}
        response = self.client.post(reverse('author-list'), author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_author_create_with_auth_returns_201(self):
        """
        Test author creation with authentication returns 201.
        """
        # FIXED: Added self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        author_data = {'name': 'New Author'}
        response = self.client.post(reverse('author-list'), author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FilterSearchTests(BaseAPITestCase):
    """
    Test filtering and search functionality.
    """
    
    def test_filter_books_by_author(self):
        """
        Test filtering books by author.
        """
        response = self.client.get(reverse('book-list'), {'author': self.author.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_search_books_by_title(self):
        """
        Test searching books by title.
        """
        response = self.client.get(reverse('book-list'), {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_order_books_by_title(self):
        """
        Test ordering books by title.
        """
        response = self.client.get(reverse('book-list'), {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ErrorHandlingTests(BaseAPITestCase):
    """
    Test error handling and status codes.
    """
    
    def test_nonexistent_book_returns_404(self):
        """
        Test nonexistent book returns 404.
        """
        response = self.client.get(reverse('book-detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_data_returns_400(self):
        """
        Test invalid data returns 400.
        """
        # FIXED: Added self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        invalid_data = {'title': '', 'publication_year': 'invalid'}
        response = self.client.post(reverse('book-create'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)