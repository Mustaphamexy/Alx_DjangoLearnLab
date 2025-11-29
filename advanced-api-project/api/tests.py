"""
Comprehensive unit tests for Django REST Framework APIs - FIXED VERSION
"""

import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework import status
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class BaseAPITestCase(APITestCase):
    """
    Base test case with common setup methods for all API tests.
    """
    
    def setUp(self):
        """
        Set up test data and clients for all test cases.
        """
        # Create test users
        self.normal_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            email='admin@example.com',
            is_staff=True
        )
        
        # Create test authors
        self.author1 = Author.objects.create(name='J.K. Rowling')
        self.author2 = Author.objects.create(name='George Orwell')
        self.author3 = Author.objects.create(name='J.R.R. Tolkien')
        
        # Create test books
        self.book1 = Book.objects.create(
            title='Harry Potter and the Philosopher\'s Stone',
            publication_year=1997,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title='1984',
            publication_year=1949,
            author=self.author2
        )
        self.book3 = Book.objects.create(
            title='Animal Farm',
            publication_year=1945,
            author=self.author2
        )
        self.book4 = Book.objects.create(
            title='The Hobbit',
            publication_year=1937,
            author=self.author3
        )
        
        # Create API client
        self.client = APIClient()
        
        # Define URLs
        self.book_list_url = reverse('book-list')
        self.book_create_url = reverse('book-create')
        self.author_list_url = reverse('author-list')
        self.author_detail_url = reverse('author-detail', kwargs={'pk': self.author1.pk})
        self.api_root_url = reverse('api-root')


class BookCRUDTests(BaseAPITestCase):
    """
    Test CRUD operations for Book model endpoints - FIXED VERSION.
    """
    
    def test_retrieve_book_list_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve book list.
        Expected: HTTP 200 OK with all books
        """
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(len(response.data['results']), 4)
    
    def test_retrieve_single_book_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve a single book.
        Expected: HTTP 200 OK with book details
        """
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['publication_year'], self.book1.publication_year)
        self.assertEqual(response.data['author'], self.author1.pk)
    
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
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_book_authenticated(self):
        """
        Test that authenticated users can create books.
        Expected: HTTP 201 Created with book data
        """
        self.client.force_authenticate(user=self.normal_user)
        
        book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Book created successfully')
        self.assertEqual(response.data['data']['title'], 'New Test Book')
        self.assertEqual(Book.objects.count(), 5)  # Original 4 + new 1
    
    def test_create_book_validation_future_year(self):
        """
        Test that book creation validates publication_year correctly.
        Expected: HTTP 400 Bad Request for future publication year
        """
        self.client.force_authenticate(user=self.normal_user)
        
        book_data = {
            'title': 'Future Book',
            'publication_year': 2030,  # Future year
            'author': self.author1.pk
        }
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
    
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
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_book_authenticated(self):
        """
        Test that authenticated users can update books.
        Expected: HTTP 200 OK with updated book data
        """
        self.client.force_authenticate(user=self.normal_user)
        
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        update_data = {
            'title': 'Updated Title',
            'publication_year': 2000,
            'author': self.author1.pk
        }
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Book updated successfully')
        self.assertEqual(response.data['data']['title'], 'Updated Title')
        
        # Verify the book was actually updated in the database
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Title')
    
    def test_partial_update_book_authenticated(self):
        """
        Test that authenticated users can partially update books.
        Expected: HTTP 200 OK with updated book data
        """
        self.client.force_authenticate(user=self.normal_user)
        
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        update_data = {
            'title': 'Partially Updated Title',
        }
        
        # FIX: Use PATCH for partial updates with format='json'
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Book updated successfully')
        self.assertEqual(response.data['data']['title'], 'Partially Updated Title')
        
        # Verify the book was actually updated in the database
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Partially Updated Title')
        # Other fields should remain unchanged
        self.assertEqual(self.book1.publication_year, 1997)
    
    def test_delete_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot delete books.
        Expected: HTTP 403 Forbidden
        """
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 4)  # No books should be deleted
    
    def test_delete_book_authenticated(self):
        """
        Test that authenticated users can delete books.
        Expected: HTTP 204 No Content
        """
        self.client.force_authenticate(user=self.normal_user)
        
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], f'Book "{self.book1.title}" deleted successfully')
        self.assertEqual(Book.objects.count(), 3)  # One book should be deleted


class AuthorCRUDTests(BaseAPITestCase):
    """
    Test CRUD operations for Author model endpoints - FIXED VERSION.
    """
    
    def test_retrieve_author_list_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve author list.
        Expected: HTTP 200 OK with all authors
        """
        response = self.client.get(self.author_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 3 authors
    
    def test_retrieve_author_detail_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve author details.
        Expected: HTTP 200 OK with author details and nested books
        """
        response = self.client.get(self.author_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.author1.name)
        self.assertIn('books', response.data)  # Should include nested books
    
    def test_create_author_unauthenticated(self):
        """
        Test that unauthenticated users cannot create authors.
        Expected: HTTP 403 Forbidden
        """
        author_data = {'name': 'New Test Author'}
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.post(self.author_list_url, author_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_author_authenticated(self):
        """
        Test that authenticated users can create authors.
        Expected: HTTP 201 Created
        """
        self.client.force_authenticate(user=self.normal_user)
        
        author_data = {'name': 'New Test Author'}
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.post(self.author_list_url, author_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 4)  # Original 3 + new 1


class FilteringSearchOrderingTests(BaseAPITestCase):
    """
    Test filtering, searching, and ordering functionalities - FIXED VERSION.
    """
    
    def test_filter_books_by_author(self):
        """
        Test filtering books by specific author.
        Expected: Only books by specified author returned
        """
        response = self.client.get(self.book_list_url, {'author': self.author2.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # author2 has 2 books
        for book in response.data['results']:
            self.assertEqual(book['author'], self.author2.pk)
    
    def test_filter_books_by_publication_year_range(self):
        """
        Test filtering books by publication year range.
        Expected: Only books within specified year range returned
        """
        response = self.client.get(
            self.book_list_url,
            {
                'publication_year_min': 1940,
                'publication_year_max': 1950
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books published between 1940-1950
        for book in response.data['results']:
            self.assertTrue(1940 <= book['publication_year'] <= 1950)
    
    def test_search_books_by_title(self):
        """
        Test searching books by title.
        Expected: Books matching search term returned
        """
        response = self.client.get(self.book_list_url, {'search': 'Harry'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn('Harry', response.data['results'][0]['title'])
    
    def test_search_books_by_author_name(self):
        """
        Test searching books by author name.
        Expected: Books by authors matching search term returned
        """
        response = self.client.get(self.book_list_url, {'search': 'Orwell'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # 2 books by Orwell
    
    def test_order_books_by_title_ascending(self):
        """
        Test ordering books by title in ascending order.
        Expected: Books returned in alphabetical order by title
        """
        response = self.client.get(self.book_list_url, {'ordering': 'title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles))
    
    def test_order_books_by_publication_year_descending(self):
        """
        Test ordering books by publication year in descending order.
        Expected: Books returned from newest to oldest
        """
        response = self.client.get(self.book_list_url, {'ordering': '-publication_year'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, sorted(years, reverse=True))
    
    def test_combined_filter_search_order(self):
        """
        Test combining filtering, searching, and ordering.
        Expected: Correctly filtered, searched, and ordered results
        """
        response = self.client.get(
            self.book_list_url,
            {
                'author': self.author2.pk,  # Filter by author
                'ordering': '-publication_year',  # Order by year descending
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # author2 has 2 books
        
        # Check ordering (should be newest first)
        results = response.data['results']
        self.assertEqual(results[0]['publication_year'], 1949)  # 1984
        self.assertEqual(results[1]['publication_year'], 1945)  # Animal Farm
    
    def test_case_insensitive_title_filter(self):
        """
        Test case-insensitive partial title matching.
        Expected: Case-insensitive matches returned
        """
        response = self.client.get(self.book_list_url, {'title_icontains': 'harry'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn('Harry', response.data['results'][0]['title'])


class PermissionAndAuthenticationTests(BaseAPITestCase):
    """
    Test permission and authentication mechanisms - FIXED VERSION.
    """
    
    def test_api_root_access_unauthenticated(self):
        """
        Test that API root is accessible without authentication.
        Expected: HTTP 200 OK
        """
        response = self.client.get(self.api_root_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('authors', response.data)
        self.assertIn('books', response.data)
    
    def test_mixed_permissions_on_author_endpoints(self):
        """
        Test that author endpoints have different permissions for different methods.
        Expected: GET allowed without auth, POST requires auth
        """
        # GET should work without authentication
        response = self.client.get(self.author_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # POST should require authentication
        author_data = {'name': 'New Author'}
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.post(self.author_list_url, author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # POST should work with authentication
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.author_list_url, author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_author_detail_permissions(self):
        """
        Test that author detail endpoint has different permissions for different methods.
        Expected: GET allowed without auth, PUT/DELETE require auth
        """
        url = reverse('author-detail', kwargs={'pk': self.author1.pk})
        
        # GET should work without authentication
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PUT should require authentication
        update_data = {'name': 'Updated Author Name'}
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # PUT should work with authentication
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # DELETE should require authentication
        self.client.force_authenticate(user=None)  # Logout
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # DELETE should work with authentication
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ErrorHandlingTests(BaseAPITestCase):
    """
    Test error handling and edge cases - FIXED VERSION.
    """
    
    def test_retrieve_nonexistent_book(self):
        """
        Test retrieving a book that doesn't exist.
        Expected: HTTP 404 Not Found
        """
        url = reverse('book-detail', kwargs={'pk': 9999})  # Non-existent ID
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_nonexistent_book(self):
        """
        Test updating a book that doesn't exist.
        Expected: HTTP 404 Not Found
        """
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('book-update', kwargs={'pk': 9999})
        update_data = {
            'title': 'Updated Title',
            'publication_year': 2000,
            'author': self.author1.pk
        }
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_book_data_creation(self):
        """
        Test creating a book with invalid data.
        Expected: HTTP 400 Bad Request
        """
        self.client.force_authenticate(user=self.normal_user)
        
        invalid_data = {
            'title': '',  # Empty title
            'publication_year': 'invalid_year',  # Invalid year format
            'author': 9999  # Non-existent author
        }
        
        # FIX: Use format='json' to set proper Content-Type
        response = self.client.post(self.book_create_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('publication_year', response.data)
        self.assertIn('author', response.data)


class BulkOperationsTests(BaseAPITestCase):
    """
    Test bulk operations functionality - FIXED VERSION.
    """
    
    def test_bulk_create_books_authenticated(self):
        """
        Test bulk creation of books by authenticated users.
        Expected: HTTP 207 Multi-Status with creation results
        """
        self.client.force_authenticate(user=self.normal_user)
        
        bulk_data = {
            'books': [
                {
                    'title': 'Bulk Book 1',
                    'publication_year': 2020,
                    'author': self.author1.pk
                },
                {
                    'title': 'Bulk Book 2',
                    'publication_year': 2021,
                    'author': self.author2.pk
                },
                {
                    'title': '',  # Invalid - empty title
                    'publication_year': 2030,  # Invalid - future year
                    'author': self.author1.pk
                }
            ]
        }
        
        url = reverse('book-bulk')
        # FIX: Already using format='json' which is correct
        response = self.client.post(url, bulk_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(len(response.data['created']), 2)  # 2 successful creations
        self.assertEqual(len(response.data['errors']), 1)   # 1 error
        self.assertEqual(Book.objects.count(), 6)  # Original 4 + 2 new


class SerializerValidationTests(TestCase):
    """
    Test serializer validation logic - FIXED VERSION.
    """
    
    def setUp(self):
        self.author = Author.objects.create(name='Test Author')
    
    def test_book_serializer_future_publication_year_validation(self):
        """
        Test that BookSerializer validates against future publication years.
        Expected: Validation error for future years
        """
        from datetime import datetime
        
        future_year = datetime.now().year + 1
        book_data = {
            'title': 'Future Book',
            'publication_year': future_year,
            'author': self.author.pk
        }
        
        serializer = BookSerializer(data=book_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('publication_year', serializer.errors)
    
    def test_book_serializer_valid_data(self):
        """
        Test that BookSerializer accepts valid data.
        Expected: Validation passes
        """
        book_data = {
            'title': 'Valid Book',
            'publication_year': 2020,
            'author': self.author.pk
        }
        
        serializer = BookSerializer(data=book_data)
        
        self.assertTrue(serializer.is_valid())
    
    def test_author_serializer_with_books(self):
        """
        Test that AuthorSerializer includes nested books.
        Expected: Serialized data includes books field
        """
        # Create books for the author
        Book.objects.create(title='Book 1', publication_year=2020, author=self.author)
        Book.objects.create(title='Book 2', publication_year=2021, author=self.author)
        
        serializer = AuthorSerializer(self.author)
        
        self.assertIn('books', serializer.data)
        self.assertEqual(len(serializer.data['books']), 2)