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
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.author = Author.objects.create(name='Test Author')
        self.book = Book.objects.create(
            title='Test Book',
            publication_year=2020,
            author=self.author
        )
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
        # FIXED: Added response.data check
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
    
    def test_book_detail_returns_correct_status(self):
        """
        Test book detail returns correct status code.
        """
        response = self.client.get(reverse('book-detail', kwargs={'pk': self.book.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # FIXED: Added response.data check
        self.assertEqual(response.data['title'], 'Test Book')
    
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
        # FIXED: Added response.data check
        self.assertIn('detail', response.data)
    
    def test_book_create_with_auth_returns_201(self):
        """
        Test book creation with authentication returns 201.
        """
        self.client.force_authenticate(user=self.user)
        book_data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author.pk
        }
        response = self.client.post(reverse('book-create'), book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # FIXED: Added response.data check
        self.assertEqual(response.data['message'], 'Book created successfully')
    
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
        # FIXED: Added response.data check
        self.assertIn('detail', response.data)
    
    def test_book_delete_without_auth_returns_403(self):
        """
        Test book delete without authentication returns 403.
        """
        response = self.client.delete(reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # FIXED: Added response.data check
        self.assertIn('detail', response.data)
    
    def test_book_delete_with_auth_returns_204(self):
        """
        Test book delete with authentication returns 204.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # FIXED: Added response.data check
        self.assertEqual(response.data['message'], 'Book "Test Book" deleted successfully')


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
        # FIXED: Added response.data check
        self.assertIsInstance(response.data, list)
    
    def test_author_create_without_auth_returns_403(self):
        """
        Test author creation without authentication returns 403.
        """
        author_data = {'name': 'New Author'}
        response = self.client.post(reverse('author-list'), author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # FIXED: Added response.data check
        self.assertIn('detail', response.data)
    
    def test_author_create_with_auth_returns_201(self):
        """
        Test author creation with authentication returns 201.
        """
        self.client.force_authenticate(user=self.user)
        author_data = {'name': 'New Author'}
        response = self.client.post(reverse('author-list'), author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # FIXED: Added response.data check
        self.assertEqual(response.data['name'], 'New Author')


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
        # FIXED: Added response.data check
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
    
    def test_search_books_by_title(self):
        """
        Test searching books by title.
        """
        response = self.client.get(reverse('book-list'), {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # FIXED: Added response.data check
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
    
    def test_order_books_by_title(self):
        """
        Test ordering books by title.
        """
        response = self.client.get(reverse('book-list'), {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # FIXED: Added response.data check
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)


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
        # FIXED: Added response.data check
        self.assertIn('detail', response.data)
    
    def test_invalid_data_returns_400(self):
        """
        Test invalid data returns 400.
        """
        self.client.force_authenticate(user=self.user)
        invalid_data = {'title': '', 'publication_year': 'invalid'}
        response = self.client.post(reverse('book-create'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # FIXED: Added response.data check
        self.assertIn('publication_year', response.data)


class BulkOperationsTests(BaseAPITestCase):
    """
    Test bulk operations.
    """
    
    def test_bulk_create_books_authenticated(self):
        """
        Test bulk creation of books by authenticated users.
        """
        self.client.force_authenticate(user=self.user)
        
        bulk_data = {
            'books': [
                {
                    'title': 'Bulk Book 1',
                    'publication_year': 2020,
                    'author': self.author.pk
                },
                {
                    'title': 'Bulk Book 2', 
                    'publication_year': 2021,
                    'author': self.author.pk
                }
            ]
        }
        
        response = self.client.post(reverse('book-bulk'), bulk_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_207_MULTI_STATUS)
        # FIXED: Added response.data check
        self.assertIn('created', response.data)
        self.assertIn('errors', response.data)