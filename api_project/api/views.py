from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Book
from .serializers import BookSerializer

# Custom permission class (optional)
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff

# Keep the existing ListAPIView for backward compatibility
class BookList(generics.ListAPIView):
    """
    API view to retrieve list of all books (read-only)
    - Publicly accessible (no authentication required)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Allow anyone to view books

# New ViewSet for full CRUD operations
class BookViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Book instances.
    Provides full CRUD operations: list, create, retrieve, update, destroy
    
    Permissions:
    - Admin users: Full CRUD access
    - Authenticated users: Read-only access  
    - Anonymous users: No access
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            # Allow any authenticated user to view books
            permission_classes = [IsAuthenticated]
        else:
            # Only allow admin users to create, update, or delete books
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]