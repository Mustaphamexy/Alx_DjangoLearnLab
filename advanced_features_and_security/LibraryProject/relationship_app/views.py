from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.http import HttpResponseForbidden
from .models import Book, Library, UserProfile, Author, CustomUser
from .forms import CustomUserCreationForm, BookForm, CustomAuthenticationForm

# Helper functions for user_passes_test
def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

def is_librarian(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'librarian'

def is_member(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'member'

# Existing views with permission checks
def list_books(request):
    """Function-based view to display all books - requires can_view permission"""
    # Check if user has permission to view books
    if not request.user.has_perm('relationship_app.can_view'):
        return HttpResponseForbidden("You don't have permission to view books.")
    
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/list_books.html', {
        'books': books,
        'can_add_book': request.user.has_perm('relationship_app.can_add_book'),
        'can_create': request.user.has_perm('relationship_app.can_create'),
        'can_edit': request.user.has_perm('relationship_app.can_edit'),
        'can_delete': request.user.has_perm('relationship_app.can_delete'),
    })

class LibraryDetailView(DetailView):
    """Class-based view to display details of a specific library"""
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
    
    def dispatch(self, request, *args, **kwargs):
        # Check permission before displaying library details
        if not request.user.has_perm('relationship_app.can_view_library'):
            return HttpResponseForbidden("You don't have permission to view library details.")
        return super().dispatch(request, *args, **kwargs)

class LibraryListView(ListView):
    """Class-based view to display all libraries"""
    model = Library
    template_name = 'relationship_app/library_list.html'
    context_object_name = 'libraries'
    
    def dispatch(self, request, *args, **kwargs):
        # Check permission before displaying library list
        if not request.user.has_perm('relationship_app.can_view_library'):
            return HttpResponseForbidden("You don't have permission to view libraries.")
        return super().dispatch(request, *args, **kwargs)

# Authentication Views (updated for custom user)
def register_view(request):
    """User registration view using custom user model"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('relationship_app:list_books')
    else:
        form = CustomUserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})

def login_view(request):
    """User login view - works with custom user model"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect('relationship_app:list_books')
    else:
        form = CustomAuthenticationForm()
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

# Role-Based Views (updated to use @user_passes_test)
@login_required
@user_passes_test(is_admin, login_url='/relationship/login/')
def admin_view(request):
    """Admin-only view"""
    users = UserProfile.objects.all().select_related('user')
    return render(request, 'relationship_app/admin_view.html', {
        'users': users,
        'total_users': users.count()
    })

@login_required
@user_passes_test(is_librarian, login_url='/relationship/login/')
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
@user_passes_test(is_member, login_url='/relationship/login/')
def member_view(request):
    """Member-only view"""
    available_books = Book.objects.all()
    libraries = Library.objects.all()
    return render(request, 'relationship_app/member_view.html', {
        'available_books': available_books,
        'libraries': libraries
    })

@login_required
@user_passes_test(is_admin, login_url='/relationship/login/')
def manage_roles(request):
    """Admin view to manage user roles"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        try:
            user_profile = UserProfile.objects.get(id=user_id)
            user_profile.role = new_role
            user_profile.save()
            messages.success(request, f'Role updated for {user_profile.user.email}')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User not found')
    
    users = UserProfile.objects.all().select_related('user')
    return render(request, 'relationship_app/manage_roles.html', {'users': users})

# Book Management Views with Custom Permissions - UPDATED WITH NEW PERMISSIONS
@login_required
@permission_required('relationship_app.can_create', raise_exception=True)
def add_book(request):
    """View to add a new book (requires can_create permission)"""
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
@permission_required('relationship_app.can_edit', raise_exception=True)
def edit_book(request, pk):
    """View to edit an existing book (requires can_edit permission)"""
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
@permission_required('relationship_app.can_delete', raise_exception=True)
def delete_book(request, pk):
    """View to delete a book (requires can_delete permission)"""
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
@permission_required('relationship_app.can_edit', raise_exception=True)
def book_management(request):
    """Book management dashboard for users with edit permissions"""
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/book_management.html', {
        'books': books,
        'can_create': request.user.has_perm('relationship_app.can_create'),
        'can_delete': request.user.has_perm('relationship_app.can_delete')
    })

# New views for library management with permissions
@login_required
@permission_required('relationship_app.can_create_library', raise_exception=True)
def add_library(request):
    """View to add a new library (requires can_create_library permission)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            library = Library.objects.create(name=name)
            messages.success(request, f'Library "{library.name}" created successfully!')
            return redirect('relationship_app:library_list')
    return render(request, 'relationship_app/add_library.html')

@login_required
@permission_required('relationship_app.can_edit_library', raise_exception=True)
def edit_library(request, pk):
    """View to edit a library (requires can_edit_library permission)"""
    library = get_object_or_404(Library, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            library.name = name
            library.save()
            messages.success(request, f'Library "{library.name}" updated successfully!')
            return redirect('relationship_app:library_list')
    
    return render(request, 'relationship_app/edit_library.html', {'library': library})

@login_required
@permission_required('relationship_app.can_delete_library', raise_exception=True)
def delete_library(request, pk):
    """View to delete a library (requires can_delete_library permission)"""
    library = get_object_or_404(Library, pk=pk)
    
    if request.method == 'POST':
        library_name = library.name
        library.delete()
        messages.success(request, f'Library "{library_name}" deleted successfully!')
        return redirect('relationship_app:library_list')
    
    return render(request, 'relationship_app/delete_library.html', {'library': library})