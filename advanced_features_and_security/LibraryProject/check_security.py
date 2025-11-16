#!/usr/bin/env python
"""
Security Check Script for Django Application
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from django.conf import settings
from django.core.checks import run_checks

def check_security_settings():
    """Check security-related settings"""
    print("=== SECURITY SETTINGS CHECK ===")
    
    security_checks = {
        'DEBUG mode': not settings.DEBUG,
        'HTTPS Redirect': settings.SECURE_SSL_REDIRECT,
        'HSTS Enabled': settings.SECURE_HSTS_SECONDS > 0,
        'Secure Session Cookies': settings.SESSION_COOKIE_SECURE,
        'Secure CSRF Cookies': settings.CSRF_COOKIE_SECURE,
        'HTTPOnly Session Cookies': settings.SESSION_COOKIE_HTTPONLY,
        'X-Frame-Options': settings.X_FRAME_OPTIONS == 'DENY',
        'Content Type NoSniff': settings.SECURE_CONTENT_TYPE_NOSNIFF,
        'XSS Filter': settings.SECURE_BROWSER_XSS_FILTER,
    }
    
    all_passed = True
    for check, passed in security_checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")
        if not passed:
            all_passed = False
    
    return all_passed

def run_django_checks():
    """Run Django system checks"""
    print("\n=== DJANGO SYSTEM CHECKS ===")
    errors = run_checks()
    
    if errors:
        print(f"Found {len(errors)} issues:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ No system check errors")
        return True

if __name__ == "__main__":
    print("Running Security Configuration Check...")
    
    security_passed = check_security_settings()
    django_passed = run_django_checks()
    
    if security_passed and django_passed:
        print("\n🎉 All security checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some security checks failed!")
        sys.exit(1)