# Django REST Framework API Project

## New API Endpoint Implementation

We've successfully implemented a Book List API endpoint.

### Files Created/Modified:

1. **`api/serializers.py`** - BookSerializer class
2. **`api/views.py`** - BookList view (ListAPIView)
3. **`api/urls.py`** - URL routing for the API
4. **`api_project/urls.py`** - Updated to include API routes
5. **`api/management/commands/seed_books.py`** - Sample data seeder

### Testing the API:

1. **Apply migrations and create sample data:**
   ```bash
   python manage.py migrate
   python manage.py seed_books 
   ```

   
## Step 8: Run the Complete Setup

```bash
# Make sure you're in the project root directory
cd api_project

# Apply migrations
python manage.py migrate

# Create sample data
python manage.py seed_books

# Verify setup
python verify_setup.py

# Start server and test
python manage.py runserver

# In another terminal, test the API
python test_api.py


## CRUD Operations with ViewSets and Routers

We've implemented full CRUD (Create, Read, Update, Delete) operations using Django REST Framework's ViewSets and Routers.

### Files Updated:

1. **`api/views.py`** - Added `BookViewSet` (ModelViewSet)
2. **`api/urls.py`** - Configured router for ViewSet endpoints
3. **`test_crud_operations.py`** - Comprehensive CRUD testing script

### API Endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/` | List all books (read-only ListAPIView) |
| GET | `/api/books_all/` | List all books (ViewSet) |
| POST | `/api/books_all/` | Create a new book |
| GET | `/api/books_all/<id>/` | Retrieve a specific book |
| PUT | `/api/books_all/<id>/` | Fully update a book |
| PATCH | `/api/books_all/<id>/` | Partially update a book |
| DELETE | `/api/books_all/<id>/` | Delete a book |


## Step 6: Run the Implementation

```bash
# Make sure you're in the project root directory
cd C:\Users\hp\Documents\VSCode\ALX-Backend\api_project

# Apply migrations (if needed)
python manage.py migrate

# Add sample data
python manage.py seed_books

# Verify setup
python verify_setup.py

# Start server
python manage.py runserver

# In another terminal, test CRUD operations
python test_crud_operations.py