#!/usr/bin/env python
import os
import sys
import django
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project.settings')

try:
    django.setup()
    
    # Import Django test client after setup
    from django.test import Client
    from django.contrib.auth.models import User
    from rest_framework.authtoken.models import Token
except Exception as e:
    print(f"❌ Error setting up Django: {e}")
    sys.exit(1)

def test_authentication():
    """Test authentication and permissions on the BookViewSet"""
    print("🔐 Testing Authentication and Permissions")
    print("=" * 60)
    
    client = Client()
    base_url = '/api'
    
    # Test data
    new_book = {
        "title": "Authentication Test Book",
        "author": "Test Author"
    }
    
    try:
        # 1. TEST UNAUTHENTICATED ACCESS TO PROTECTED ENDPOINTS
        print("\n1. 🚫 Testing Unauthenticated Access")
        print("-" * 40)
        
        # Try to access books_all without authentication
        response = client.get(f'{base_url}/books_all/')
        if response.status_code == 401:
            print("✅ Unauthenticated access correctly blocked")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
        
        # 2. TEST TOKEN AUTHENTICATION
        print("\n2. 🔑 Testing Token Authentication")
        print("-" * 40)
        
        # Get or create test user and token
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'password': 'testpass123'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        token, created = Token.objects.get_or_create(user=user)
        
        # Test with token in header
        response = client.get(
            f'{base_url}/books_all/',
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        
        if response.status_code == 200:
            print("✅ Token authentication successful")
            books = response.json()
            print(f"   Retrieved {len(books)} books with token")
        else:
            print(f"❌ Token authentication failed - Status: {response.status_code}")
            return False
        
        # 3. TEST PERMISSIONS FOR REGULAR USER (READ-ONLY)
        print("\n3. 👤 Testing Regular User Permissions (Read-Only)")
        print("-" * 40)
        
        # Try to create a book as regular user (should fail)
        response = client.post(
            f'{base_url}/books_all/',
            data=json.dumps(new_book),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        
        if response.status_code == 403:
            print("✅ Regular user correctly blocked from creating books")
        else:
            print(f"❌ Expected 403 for regular user, got {response.status_code}")
            return False
        
        # 4. TEST ADMIN USER PERMISSIONS (FULL ACCESS)
        print("\n4. 👑 Testing Admin User Permissions (Full Access)")
        print("-" * 40)
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        
        admin_token, created = Token.objects.get_or_create(user=admin_user)
        
        # Create a book as admin (should succeed)
        response = client.post(
            f'{base_url}/books_all/',
            data=json.dumps(new_book),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {admin_token.key}'
        )
        
        if response.status_code == 201:
            created_book = response.json()
            book_id = created_book['id']
            print("✅ Admin user successfully created a book")
            print(f"   Created book ID: {book_id}")
        else:
            print(f"❌ Admin user failed to create book - Status: {response.status_code}")
            return False
        
        # 5. TEST PUBLIC ACCESS TO BOOKS ENDPOINT
        print("\n5. 🌐 Testing Public Access to /books/ endpoint")
        print("-" * 40)
        
        response = client.get(f'{base_url}/books/')
        if response.status_code == 200:
            books = response.json()
            print("✅ Public books endpoint accessible without authentication")
            print(f"   Retrieved {len(books)} books")
        else:
            print(f"❌ Public books endpoint failed - Status: {response.status_code}")
            return False
        
        # 6. TEST TOKEN OBTAIN ENDPOINT
        print("\n6. 🎫 Testing Token Obtain Endpoint")
        print("-" * 40)
        
        response = client.post(
            f'{base_url}/auth-token/',
            data={'username': 'testuser', 'password': 'testpass123'},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Token obtain endpoint working")
            print(f"   Received token: {token_data['token'][:10]}...")
        else:
            print(f"❌ Token obtain failed - Status: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL AUTHENTICATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during authentication testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_authentication_endpoints():
    """Display authentication-related endpoints"""
    print("\n🔐 Authentication Endpoints:")
    print("-" * 40)
    base_url = "http://127.0.0.1:8000/api"
    
    endpoints = [
        ("POST   ", f"{base_url}/auth-token/", "Obtain authentication token"),
        ("GET    ", f"{base_url}/books/", "Public books list (no auth)"),
        ("GET    ", f"{base_url}/books_all/", "Protected books list (token required)"),
        ("POST   ", f"{base_url}/books_all/", "Create book (admin token required)"),
    ]
    
    for method, url, description in endpoints:
        print(f"{method} {url:<35} {description}")
    
    print("\n👥 Sample Users (after running create_users):")
    print("   Admin:  username='admin'  password='admin123'")
    print("   User:   username='user'   password='user123'")

if __name__ == "__main__":
    show_authentication_endpoints()
    print("\n")
    if test_authentication():
        print("\n🚀 Authentication Implementation Complete!")
        print("\n💡 Next steps:")
        print("   1. Run 'python manage.py create_users' to create sample users")
        print("   2. Use the tokens in your API requests")
        print("   3. Test with different user roles")
    else:
        print("\n❌ Authentication Testing Failed!")
        sys.exit(1)