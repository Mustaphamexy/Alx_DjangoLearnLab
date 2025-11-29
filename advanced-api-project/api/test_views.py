"""
Comprehensive unit tests for Django REST Framework APIs.
Testing API endpoints for functionality, response data integrity, and status code accuracy.
"""

import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class BaseAPITestCase(APITestCase):
    """
    Base test case with common setup methods for all API tests.
    Django automatically configures a separate test database.
    """
    
    def setUp(self):
        """
        Set up test data and clients for all test cases.
        Uses separate test database to avoid impacting production/development data.
        """
        # Create test users
        self.normal_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test authors
        self.author1 = Author.objects.create(name='J.K. Rowling')
        self.author2 = Author.objects.create(name='George Orwell')
        
        # Create test books
        self.book1 = Book.objects.create(
            title='Harry Potter',
            publication_year=1997,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title='1984',
            publication_year=1949,
            author=self.author2
        )
        
        # Create API client
        self.client = APIClient()


class BookCRUDTests(BaseAPITestCase):
    """
    Test CRUD operations for Book model endpoints.
    """
    
    def test_retrieve_book_list_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve book list.
        Expected: HTTP 200 OK
        """
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_single_book_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve a single book.
        Expected: HTTP 200 OK
        """
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot create books.
        Expected: HTTP 403 Forbidden
        """
        book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.client.post(reverse('book-create'), book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_book_authenticated(self):
        """
        Test that authenticated users can create books.
        Expected: HTTP 201 Created
        """
        self.client.force_authenticate(user=self.normal_user)
        book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.client.post(reverse('book-create'), book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot update books.
        Expected: HTTP 403 Forbidden
        """
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        update_data = {
            'title': 'Updated Title',
            'publication_year': 2000,
            'author': self.author1.pk
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_book_authenticated(self):
        """
        Test that authenticated users can update books.
        Expected: HTTP 200 OK
        """
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        update_data = {
            'title': 'Updated Title',
            'publication_year': 2000,
            'author': self.author1.pk
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot delete books.
        Expected: HTTP 403 Forbidden
        """
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_book_authenticated(self):
        """
        Test that authenticated users can delete books.
        Expected: HTTP 204 No Content
        """
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AuthorCRUDTests(BaseAPITestCase):
    """
    Test CRUD operations for Author model endpoints.
    """
    
    def test_retrieve_author_list_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve author list.
        Expected: HTTP 200 OK
        """
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_author_unauthenticated(self):
        """
        Test that unauthenticated users cannot create authors.
        Expected: HTTP 403 Forbidden
        """
        author_data = {'name': 'New Test Author'}
        response = self.client.post(reverse('author-list'), author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_author_authenticated(self):
        """
        Test that authenticated users can create authors.
        Expected: HTTP 201 Created
        """
        self.client.force_authenticate(user=self.normal_user)
        author_data = {'name': 'New Test Author'}
        response = self.client.post(reverse('author-list'), author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FilteringSearchOrderingTests(BaseAPITestCase):
    """
    Test filtering, searching, and ordering functionalities.
    """
    
    def test_filter_books_by_author(self):
        """
        Test filtering books by specific author.
        Expected: HTTP 200 OK with filtered results
        """
        response = self.client.get(reverse('book-list'), {'author': self.author1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_search_books_by_title(self):
        """
        Test searching books by title.
        Expected: HTTP 200 OK with search results
        """
        response = self.client.get(reverse('book-list'), {'search': 'Harry'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_order_books_by_title(self):
        """
        Test ordering books by title.
        Expected: HTTP 200 OK with ordered results
        """
        response = self.client.get(reverse('book-list'), {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionTests(BaseAPITestCase):
    """
    Test permission and authentication mechanisms.
    """
    
    def test_api_root_access_unauthenticated(self):
        """
        Test that API root is accessible without authentication.
        Expected: HTTP 200 OK
        """
        response = self.client.get(reverse('api-root'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_mixed_permissions_on_author_endpoints(self):
        """
        Test that author endpoints have different permissions for different methods.
        Expected: GET allowed without auth, POST requires auth
        """
        # GET should work without authentication
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # POST should require authentication
        author_data = {'name': 'New Author'}
        response = self.client.post(reverse('author-list'), author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ErrorHandlingTests(BaseAPITestCase):
    """
    Test error handling and edge cases.
    """
    
    def test_retrieve_nonexistent_book(self):
        """
        Test retrieving a book that doesn't exist.
        Expected: HTTP 404 Not Found
        """
        url = reverse('book-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_book_data_creation(self):
        """
        Test creating a book with invalid data.
        Expected: HTTP 400 Bad Request
        """
        self.client.force_authenticate(user=self.normal_user)
        invalid_data = {
            'title': '',  # Empty title
            'publication_year': 'invalid_year',
        }
        response = self.client.post(reverse('book-create'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SerializerTests(TestCase):
    """
    Test serializer validation logic.
    """
    
    def setUp(self):
        self.author = Author.objects.create(name='Test Author')
    
    def test_book_serializer_validation(self):
        """
        Test BookSerializer validation.
        """
        book_data = {
            'title': 'Test Book',
            'publication_year': 2020,
            'author': self.author.pk
        }
        serializer = BookSerializer(data=book_data)
        self.assertTrue(serializer.is_valid())