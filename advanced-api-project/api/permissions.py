"""
Custom permission classes for the Advanced API Project.

This module defines custom permission classes for fine-grained access control
beyond Django REST Framework's built-in permissions.
"""

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.owner == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    """
    Custom permission to allow:
    - Anyone to create objects
    - Only authenticated users to read/update/delete
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_authenticated