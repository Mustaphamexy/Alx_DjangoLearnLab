#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Error setting up Django: {e}")
    sys.exit(1)

def test_crud_operations():
    """Test all CRUD operations on the BookViewSet"""
    base_url = 'http://127.0.0.1:8000/api'
    
    print("📚 Testing CRUD Operations with BookViewSet")
    print("=" * 60)
    
    # Test data
    new_book = {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien"
    }
    
    updated_book = {
        "title": "The Hobbit: There and Back Again",
        "author": "J.R.R. Tolkien"
    }
    
    try:
        # 1. TEST LIST OPERATION (GET /books_all/)
        print("\n1. 📖 Testing LIST operation (GET /books_all/)")
        print("-" * 40)
        list_url = f"{base_url}/books_all/"
        response = requests.get(list_url)
        
        if response.status_code == 200:
            books = response.json()
            print(f"✅ LIST successful - Found {len(books)} books")
            if books:
                print(f"   Sample book: '{books[0]['title']}' by {books[0]['author']}")
        else:
            print(f"❌ LIST failed - Status: {response.status_code}")
            return False
        
        # 2. TEST CREATE OPERATION (POST /books_all/)
        print("\n2. ➕ Testing CREATE operation (POST /books_all/)")
        print("-" * 40)
        create_url = f"{base_url}/books_all/"
        response = requests.post(create_url, json=new_book)
        
        if response.status_code == 201:
            created_book = response.json()
            book_id = created_book['id']
            print(f"✅ CREATE successful - Book ID: {book_id}")
            print(f"   Created: '{created_book['title']}' by {created_book['author']}")
        else:
            print(f"❌ CREATE failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 3. TEST RETRIEVE OPERATION (GET /books_all/<id>/)
        print("\n3. 🔍 Testing RETRIEVE operation (GET /books_all/<id>/)")
        print("-" * 40)
        retrieve_url = f"{base_url}/books_all/{book_id}/"
        response = requests.get(retrieve_url)
        
        if response.status_code == 200:
            retrieved_book = response.json()
            print(f"✅ RETRIEVE successful")
            print(f"   Retrieved: '{retrieved_book['title']}' by {retrieved_book['author']}")
        else:
            print(f"❌ RETRIEVE failed - Status: {response.status_code}")
            return False
        
        # 4. TEST UPDATE OPERATION (PUT /books_all/<id>/)
        print("\n4. ✏️  Testing UPDATE operation (PUT /books_all/<id>/)")
        print("-" * 40)
        update_url = f"{base_url}/books_all/{book_id}/"
        response = requests.put(update_url, json=updated_book)
        
        if response.status_code == 200:
            updated = response.json()
            print(f"✅ UPDATE successful")
            print(f"   Updated to: '{updated['title']}' by {updated['author']}")
        else:
            print(f"❌ UPDATE failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 5. TEST PARTIAL UPDATE OPERATION (PATCH /books_all/<id>/)
        print("\n5. 🎯 Testing PARTIAL UPDATE operation (PATCH /books_all/<id>/)")
        print("-" * 40)
        patch_url = f"{base_url}/books_all/{book_id}/"
        patch_data = {"title": "The Hobbit: Original Title"}
        response = requests.patch(patch_url, json=patch_data)
        
        if response.status_code == 200:
            patched = response.json()
            print(f"✅ PARTIAL UPDATE successful")
            print(f"   Title updated to: '{patched['title']}'")
            print(f"   Author remains: {patched['author']}")
        else:
            print(f"❌ PARTIAL UPDATE failed - Status: {response.status_code}")
        
        # 6. TEST DELETE OPERATION (DELETE /books_all/<id>/)
        print("\n6. 🗑️  Testing DELETE operation (DELETE /books_all/<id>/)")
        print("-" * 40)
        delete_url = f"{base_url}/books_all/{book_id}/"
        response = requests.delete(delete_url)
        
        if response.status_code == 204:
            print(f"✅ DELETE successful - Book ID {book_id} deleted")
        else:
            print(f"❌ DELETE failed - Status: {response.status_code}")
            return False
        
        # 7. VERIFY DELETE (GET /books_all/<id>/ should return 404)
        print("\n7. ✅ Verifying DELETE operation")
        print("-" * 40)
        verify_url = f"{base_url}/books_all/{book_id}/"
        response = requests.get(verify_url)
        
        if response.status_code == 404:
            print("✅ DELETE verified - Book no longer exists")
        else:
            print(f"❌ DELETE verification failed - Book still exists")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ALL CRUD OPERATIONS TESTED SUCCESSFULLY!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Make sure the development server is running.")
        print("   Run: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def show_api_endpoints():
    """Display all available API endpoints"""
    print("\n🌐 Available API Endpoints:")
    print("-" * 40)
    base_url = "http://127.0.0.1:8000/api"
    
    endpoints = [
        ("GET    ", f"{base_url}/books/", "List all books (read-only)"),
        ("GET    ", f"{base_url}/books_all/", "List all books (ViewSet)"),
        ("POST   ", f"{base_url}/books_all/", "Create a new book"),
        ("GET    ", f"{base_url}/books_all/<id>/", "Retrieve a specific book"),
        ("PUT    ", f"{base_url}/books_all/<id>/", "Update a specific book"),
        ("PATCH  ", f"{base_url}/books_all/<id>/", "Partially update a book"),
        ("DELETE ", f"{base_url}/books_all/<id>/", "Delete a specific book"),
    ]
    
    for method, url, description in endpoints:
        print(f"{method} {url:<35} {description}")

if __name__ == "__main__":
    show_api_endpoints()
    print("\n")
    if test_crud_operations():
        print("\n🚀 CRUD Implementation Complete!")
        print("\n💡 You can now use tools like curl, Postman, or your browser to test:")
        print("   - Create books with POST requests")
        print("   - Read books with GET requests") 
        print("   - Update books with PUT/PATCH requests")
        print("   - Delete books with DELETE requests")
    else:
        print("\n❌ CRUD Testing Failed!")
        sys.exit(1)