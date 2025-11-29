# API Views Documentation

## Overview
This project implements comprehensive CRUD operations using Django REST Framework's generic views with custom permissions and behavior.

## View Configuration

### Book Views
- **BookListView**: List all books (public access)
- **BookDetailView**: Retrieve single book (public access)  
- **BookCreateView**: Create new book (authenticated users only)
- **BookUpdateView**: Update existing book (authenticated users only)
- **BookDeleteView**: Delete book (authenticated users only)

### Author Views
- **AuthorListView**: List all authors or create new (read: public, write: authenticated)
- **AuthorDetailView**: Retrieve, update, or delete author (read: public, write: authenticated)

### Custom Hooks
- `perform_create()`: Custom logic before saving new instances
- `perform_update()`: Custom logic before updating instances  
- `perform_destroy()`: Custom logic before deleting instances
- `get_permissions()`: Dynamic permission handling based on HTTP method

## URL Patterns
All endpoints follow RESTful conventions with clear, descriptive URLs.

## Permissions
- Read operations: AllowAny
- Write operations: IsAuthenticated
- Custom permission classes available for advanced scenarios