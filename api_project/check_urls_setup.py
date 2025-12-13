#!/usr/bin/env python
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_setup():
    print("🔍 Checking URL Configuration Setup")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check 1: api_project/urls.py exists and includes api.urls
    print("\n1. Checking api_project/urls.py")
    project_urls_path = os.path.join('api_project', 'urls.py')
    
    if os.path.exists(project_urls_path):
        print("   ✅ api_project/urls.py exists")
        
        with open(project_urls_path, 'r') as f:
            content = f.read()
            
        if "include('api.urls')" in content or 'include("api.urls")' in content:
            print("   ✅ api_project/urls.py includes api.urls")
        else:
            print("   ❌ api_project/urls.py does NOT include api.urls")
            all_checks_passed = False
    else:
        print("   ❌ api_project/urls.py does not exist")
        all_checks_passed = False
    
    # Check 2: api/urls.py exists
    print("\n2. Checking api/urls.py")
    app_urls_path = os.path.join('api', 'urls.py')
    
    if os.path.exists(app_urls_path):
        print("   ✅ api/urls.py exists")
        
        with open(app_urls_path, 'r') as f:
            content = f.read()
            
        if "path('books/', BookList.as_view()" in content:
            print("   ✅ api/urls.py contains BookList view mapping")
        else:
            print("   ❌ api/urls.py does NOT contain BookList view mapping")
            all_checks_passed = False
    else:
        print("   ❌ api/urls.py does not exist")
        all_checks_passed = False
    
    # Check 3: path() function is used
    print("\n3. Checking path() function usage")
    
    if os.path.exists(app_urls_path):
        with open(app_urls_path, 'r') as f:
            content = f.read()
            
        if "from django.urls import path" in content or "from django.urls import include, path" in content:
            print("   ✅ path() function is imported")
        else:
            print("   ❌ path() function is NOT imported")
            all_checks_passed = False
            
        if "path(" in content:
            print("   ✅ path() function is used in URL patterns")
        else:
            print("   ❌ path() function is NOT used in URL patterns")
            all_checks_passed = False
    
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 All URL configuration checks passed!")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    check_setup()