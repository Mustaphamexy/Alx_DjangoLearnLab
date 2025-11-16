from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.utils.html import escape
from django.http import JsonResponse
from .models import Book, Author
from .forms import BookForm
import logging

# Security: Set up logger for security events
logger = logging.getLogger('django.security')

def book_list(request):
    """
    Secure book list view with safe search functionality.
    Uses Django ORM to prevent SQL injection.
    """
    books = Book.objects.all().select_related('author')
    
    # Security: Safe search with parameterized queries
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Security: Use Q objects for safe query construction
        # Security: Escape search query for logging
        safe_search_query = escape(search_query)
        logger.info(f"Book search executed: {safe_search_query}")
        
        # Security: Use Django ORM to prevent SQL injection
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__name__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    
    return render(request, 'bookshelf/book_list.html', context)

def book_detail(request, pk):
    """
    Secure book detail view.
    """
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'bookshelf/book_detail.html', {'book': book})

@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
def book_add(request):
    """
    Secure book creation view with CSRF protection and form validation.
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            logger.info(f"Book created: {book.title} by user {request.user.email}")
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('bookshelf:book_list')
        else:
            logger.warning("Book creation failed: form validation errors")
    else:
        form = BookForm()
    
    return render(request, 'bookshelf/form_example.html', {
        'form': form,
        'title': 'Add New Book',
        'action': 'Add'
    })

@login_required
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, pk):
    """
    Secure book editing view with proper authorization.
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            logger.info(f"Book edited: {book.title} by user {request.user.email}")
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('bookshelf:book_list')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'bookshelf/form_example.html', {
        'form': form,
        'title': 'Edit Book',
        'action': 'Update',
        'book': book
    })

@login_required
@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, pk):
    """
    Secure book deletion view with confirmation and logging.
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        logger.warning(f"Book deleted: {book.title} by user {request.user.email}")
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted successfully!')
        return redirect('bookshelf:book_list')
    
    return render(request, 'bookshelf/delete_confirmation.html', {
        'book': book,
        'object_type': 'book'
    })

def safe_search_api(request):
    """
    Example of a secure API endpoint with input validation.
    """
    search_term = request.GET.get('term', '').strip()
    max_results = request.GET.get('max', 10)
    
    # Security: Validate and convert max_results safely
    try:
        max_results = int(max_results)
        if max_results > 100:
            max_results = 100
        if max_results < 1:
            max_results = 10
    except (ValueError, TypeError):
        max_results = 10
    
    if search_term:
        books = Book.objects.filter(title__icontains=search_term)[:max_results]
        data = {
            'results': [
                {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author.name
                }
                for book in books
            ]
        }
        return JsonResponse(data)
    
    return JsonResponse({'results': []})