"""
Test script for manually testing the API views.
Run this script to verify all endpoints are working correctly.
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_api_root():
    """Test API root endpoint"""
    print("Testing API Root...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_book_list():
    """Test book list endpoint"""
    print("Testing Book List...")
    response = requests.get(f"{BASE_URL}/books/")
    print(f"Status: {response.status_code}")
    books = response.json()
    print(f"Found {len(books)} books")
    print()

def test_author_list():
    """Test author list endpoint"""
    print("Testing Author List...")
    response = requests.get(f"{BASE_URL}/authors/")
    print(f"Status: {response.status_code}")
    authors = response.json()
    print(f"Found {len(authors)} authors")
    print()

def test_book_detail(book_id=1):
    """Test book detail endpoint"""
    print(f"Testing Book Detail (ID: {book_id})...")
    response = requests.get(f"{BASE_URL}/books/{book_id}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        book = response.json()
        print(f"Book: {book['title']} by {book['author']}")
    print()

def test_permission_checks():
    """Test that permissions are working correctly"""
    print("Testing Permissions...")
    
    # Test unauthenticated user trying to create a book
    book_data = {
        'title': 'Unauthorized Book',
        'publication_year': 2023,
        'author': 1
    }
    response = requests.post(f"{BASE_URL}/books/create/", json=book_data)
    print(f"Unauthorized create attempt: {response.status_code} (should be 403)")
    print()

if __name__ == "__main__":
    print("=== Testing Django REST Framework Views ===\n")
    
    test_api_root()
    test_book_list()
    test_author_list()
    test_book_detail()
    test_permission_checks()
    
    print("=== Testing Complete ===")