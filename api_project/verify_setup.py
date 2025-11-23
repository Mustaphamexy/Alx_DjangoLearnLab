#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

def verify_setup():
    print("Verifying Django REST Framework Authentication Setup...")
    
    # Check if we can import key components
    try:
        from rest_framework import __version__ as drf_version
        print(f"✓ Django REST Framework {drf_version} is installed")
    except ImportError:
        print("✗ Django REST Framework is not installed")
        return False
    
    # Check authentication apps
    try:
        from rest_framework.authtoken.models import Token
        print("✓ Token authentication is available")
    except ImportError as e:
        print(f"✗ Token authentication not available: {e}")
        return False
    
    try:
        from api.models import Book
        print("✓ Book model is accessible")
    except ImportError as e:
        print(f"✗ Error accessing Book model: {e}")
        return False
    
    try:
        from api.views import BookList, BookViewSet
        print("✓ BookList and BookViewSet are accessible")
    except ImportError as e:
        print(f"✗ Error accessing views: {e}")
        return False
    
    # Test authentication configuration
    try:
        from django.conf import settings
        if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
            print("✓ Token auth app is in INSTALLED_APPS")
        else:
            print("✗ Token auth app not in INSTALLED_APPS")
            return False
            
        # Check REST framework settings
        if hasattr(settings, 'REST_FRAMEWORK'):
            auth_classes = settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])
            if 'rest_framework.authentication.TokenAuthentication' in auth_classes:
                print("✓ Token authentication is configured")
            else:
                print("✗ Token authentication not configured")
                return False
        else:
            print("✗ REST_FRAMEWORK settings not found")
            return False
            
    except Exception as e:
        print(f"✗ Error checking configuration: {e}")
        return False
    
    # Test database connection and migrations
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database is accessible")
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False
    
    # Check if tokens table exists
    try:
        Token.objects.exists()
        print("✓ Token table is accessible")
    except Exception as e:
        print(f"✗ Token table error: {e}")
        return False
    
    print("✓ All authentication components are properly set up!")
    return True

if __name__ == "__main__":
    if verify_setup():
        print("\nAuthentication setup verification successful!")
        print("\nNext steps:")
        print("1. Run 'python manage.py migrate' to create token tables")
        print("2. Run 'python manage.py create_users' to create sample users")
        print("3. Run 'python manage.py runserver'")
        print("4. Run 'python test_authentication.py' to test authentication")
        print("5. Use tokens in your API requests:")
        print("   Header: Authorization: Token <your_token_here>")
    else:
        print("\nAuthentication setup verification failed!")
        sys.exit(1)