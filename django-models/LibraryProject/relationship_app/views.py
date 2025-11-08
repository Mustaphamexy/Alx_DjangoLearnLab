from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.urls import reverse
from .models import Book, Library, UserProfile, Author
from .decorators import admin_required, librarian_required, member_required
from .forms import CustomUserCreationForm, BookForm

# Existing views (keep these)
def list_books(request):
    """Function-based view to display all books"""
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/list_books.html', {
        'books': books,
        'can_add_book': request.user.has_perm('relationship_app.can_add_book')
    })

class LibraryDetailView(DetailView):
    """Class-based view to display details of a specific library"""
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

class LibraryListView(ListView):
    """Class-based view to display all libraries"""
    model = Library
    template_name = 'relationship_app/library_list.html'
    context_object_name = 'libraries'

# Authentication Views (keep these)
def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('relationship_app:list_books')
    else:
        form = CustomUserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('relationship_app:list_books')
    else:
        form = AuthenticationForm()
    return render(request, 'relationship_app/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return render(request, 'relationship_app/logout.html')

@login_required
def profile_view(request):
    """Protected profile view that requires login"""
    return render(request, 'relationship_app/profile.html', {'user': request.user})

# Role-Based Views (keep these)
@login_required
@admin_required
def admin_view(request):
    """Admin-only view"""
    users = UserProfile.objects.all().select_related('user')
    return render(request, 'relationship_app/admin_view.html', {
        'users': users,
        'total_users': users.count()
    })

@login_required
@librarian_required
def librarian_view(request):
    """Librarian-only view"""
    libraries = Library.objects.all()
    books = Book.objects.all()
    return render(request, 'relationship_app/librarian_view.html', {
        'libraries': libraries,
        'books': books,
        'total_books': books.count()
    })

@login_required
@member_required
def member_view(request):
    """Member-only view"""
    available_books = Book.objects.all()
    libraries = Library.objects.all()
    return render(request, 'relationship_app/member_view.html', {
        'available_books': available_books,
        'libraries': libraries
    })

@login_required
@admin_required
def manage_roles(request):
    """Admin view to manage user roles"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        try:
            user_profile = UserProfile.objects.get(id=user_id)
            user_profile.role = new_role
            user_profile.save()
            messages.success(request, f'Role updated for {user_profile.user.username}')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User not found')
    
    users = UserProfile.objects.all().select_related('user')
    return render(request, 'relationship_app/manage_roles.html', {'users': users})

# Book Management Views with Custom Permissions
@login_required
@permission_required('relationship_app.can_add_book', login_url='/relationship/login/')
def add_book(request):
    """View to add a new book (requires can_add_book permission)"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('relationship_app:list_books')
    else:
        form = BookForm()
    
    return render(request, 'relationship_app/book_form.html', {
        'form': form,
        'title': 'Add New Book',
        'action': 'Add'
    })

@login_required
@permission_required('relationship_app.can_change_book', login_url='/relationship/login/')
def edit_book(request, pk):
    """View to edit an existing book (requires can_change_book permission)"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('relationship_app:list_books')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'relationship_app/book_form.html', {
        'form': form,
        'title': 'Edit Book',
        'action': 'Update',
        'book': book
    })

@login_required
@permission_required('relationship_app.can_delete_book', login_url='/relationship/login/')
def delete_book(request, pk):
    """View to delete a book (requires can_delete_book permission)"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted successfully!')
        return redirect('relationship_app:list_books')
    
    return render(request, 'relationship_app/delete_book.html', {
        'book': book
    })

@login_required
@permission_required('relationship_app.can_change_book', login_url='/relationship/login/')
def book_management(request):
    """Book management dashboard for users with change permissions"""
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/book_management.html', {
        'books': books,
        'can_add_book': request.user.has_perm('relationship_app.can_add_book'),
        'can_delete_book': request.user.has_perm('relationship_app.can_delete_book')
    })