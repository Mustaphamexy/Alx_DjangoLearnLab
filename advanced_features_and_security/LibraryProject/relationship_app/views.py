from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Book, Library, UserProfile, Author, CustomUser, Librarian
from .forms import (CustomUserCreationForm, BookForm, CustomAuthenticationForm, 
                   AuthorForm, LibraryForm, UserProfileForm, CustomPasswordChangeForm)

# Helper functions for user_passes_test
def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

def is_librarian(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'librarian'

def is_member(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'member'

def has_role(user, roles):
    """Check if user has one of the specified roles"""
    if not hasattr(user, 'userprofile'):
        return False
    return user.userprofile.role in roles

# Dashboard and Home Views
def home_view(request):
    """Home page view"""
    if request.user.is_authenticated:
        # Redirect authenticated users based on role
        if hasattr(request.user, 'userprofile'):
            role = request.user.userprofile.role
            if role == 'admin':
                return redirect('relationship_app:admin_dashboard')
            elif role == 'librarian':
                return redirect('relationship_app:librarian_dashboard')
            elif role == 'member':
                return redirect('relationship_app:member_dashboard')
    
    # For non-authenticated users, show public home page
    recent_books = Book.objects.all().order_by('-id')[:5]
    library_count = Library.objects.count()
    book_count = Book.objects.count()
    
    return render(request, 'relationship_app/home.html', {
        'recent_books': recent_books,
        'library_count': library_count,
        'book_count': book_count,
    })

@login_required
def dashboard_view(request):
    """Universal dashboard that redirects based on role"""
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, "User profile not found. Please contact administrator.")
        return redirect('relationship_app:home')
    
    role = request.user.userprofile.role
    if role == 'admin':
        return redirect('relationship_app:admin_dashboard')
    elif role == 'librarian':
        return redirect('relationship_app:librarian_dashboard')
    elif role == 'member':
        return redirect('relationship_app:member_dashboard')
    else:
        messages.error(request, "Unknown user role.")
        return redirect('relationship_app:home')

# Book Views
def list_books(request):
    """Function-based view to display all books - requires can_view permission"""
    # Check if user has permission to view books
    if not request.user.has_perm('relationship_app.can_view'):
        return HttpResponseForbidden("You don't have permission to view books.")
    
    books = Book.objects.all().select_related('author').order_by('title')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'relationship_app/list_books.html', {
        'page_obj': page_obj,
        'query': query,
        'can_add_book': request.user.has_perm('relationship_app.can_add_book'),
        'can_create': request.user.has_perm('relationship_app.can_create'),
        'can_edit': request.user.has_perm('relationship_app.can_edit'),
        'can_delete': request.user.has_perm('relationship_app.can_delete'),
    })

class BookDetailView(DetailView):
    """Class-based view to display details of a specific book"""
    model = Book
    template_name = 'relationship_app/book_detail.html'
    context_object_name = 'book'
    
    def dispatch(self, request, *args, **kwargs):
        # Check permission before displaying book details
        if not request.user.has_perm('relationship_app.can_view'):
            return HttpResponseForbidden("You don't have permission to view book details.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.request.user.has_perm('relationship_app.can_edit')
        context['can_delete'] = self.request.user.has_perm('relationship_app.can_delete')
        return context

# Library Views
class LibraryListView(ListView):
    """Class-based view to display all libraries"""
    model = Library
    template_name = 'relationship_app/library_list.html'
    context_object_name = 'libraries'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        # Check permission before displaying library list
        if not request.user.has_perm('relationship_app.can_view_library'):
            return HttpResponseForbidden("You don't have permission to view libraries.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(book_count=Count('books'))
        return queryset

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library = self.get_object()
        context['books'] = library.books.all().select_related('author')
        context['librarians'] = library.librarians.all()
        context['can_edit_library'] = self.request.user.has_perm('relationship_app.can_edit_library')
        context['can_delete_library'] = self.request.user.has_perm('relationship_app.can_delete_library')
        return context

# Authentication Views
def register_view(request):
    """User registration view using custom user model"""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('relationship_app:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Registration successful! Welcome, {user.email}!')
            return redirect('relationship_app:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'relationship_app/register.html', {'form': form})

def login_view(request):
    """User login view - works with custom user model"""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('relationship_app:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            
            # Redirect based on role
            if hasattr(user, 'userprofile'):
                role = user.userprofile.role
                if role == 'admin':
                    return redirect('relationship_app:admin_dashboard')
                elif role == 'librarian':
                    return redirect('relationship_app:librarian_dashboard')
                elif role == 'member':
                    return redirect('relationship_app:member_dashboard')
            
            return redirect('relationship_app:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'relationship_app/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('relationship_app:home')

@login_required
def profile_view(request):
    """Protected profile view that requires login"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile, user=user)
        password_form = CustomPasswordChangeForm(user, request.POST)
        
        if 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            # Update user fields
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.date_of_birth = request.POST.get('date_of_birth') or None
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('relationship_app:profile')
        
        elif 'change_password' in request.POST and password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('relationship_app:profile')
    
    else:
        profile_form = UserProfileForm(instance=profile, user=user)
        password_form = CustomPasswordChangeForm(user)
    
    return render(request, 'relationship_app/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user': user
    })

# Role-Based Dashboard Views
@login_required
@user_passes_test(is_admin, login_url='/relationship/login/')
def admin_dashboard(request):
    """Admin-only dashboard"""
    users = UserProfile.objects.all().select_related('user').order_by('-created_at')
    total_books = Book.objects.count()
    total_libraries = Library.objects.count()
    total_users = users.count()
    
    # Recent activity
    recent_books = Book.objects.all().order_by('-id')[:5]
    recent_users = CustomUser.objects.all().order_by('-date_joined')[:5]
    
    return render(request, 'relationship_app/admin_dashboard.html', {
        'users': users[:10],  # Show only 10 most recent
        'total_users': total_users,
        'total_books': total_books,
        'total_libraries': total_libraries,
        'recent_books': recent_books,
        'recent_users': recent_users,
    })

@login_required
@user_passes_test(is_librarian, login_url='/relationship/login/')
def librarian_dashboard(request):
    """Librarian-only dashboard"""
    libraries = Library.objects.all().annotate(book_count=Count('books'))
    books = Book.objects.all().select_related('author')
    recent_books = books.order_by('-id')[:5]
    
    return render(request, 'relationship_app/librarian_dashboard.html', {
        'libraries': libraries,
        'books': books,
        'recent_books': recent_books,
        'total_books': books.count(),
        'total_libraries': libraries.count(),
    })

@login_required
@user_passes_test(is_member, login_url='/relationship/login/')
def member_dashboard(request):
    """Member-only dashboard"""
    available_books = Book.objects.all().select_related('author')
    libraries = Library.objects.all().annotate(book_count=Count('books'))
    recent_books = available_books.order_by('-id')[:5]
    
    return render(request, 'relationship_app/member_dashboard.html', {
        'available_books': available_books[:10],  # Show only 10
        'libraries': libraries,
        'recent_books': recent_books,
        'total_books': available_books.count(),
        'total_libraries': libraries.count(),
    })

# Management Views
@login_required
@user_passes_test(is_admin, login_url='/relationship/login/')
def manage_roles(request):
    """Admin view to manage user roles"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        try:
            user_profile = UserProfile.objects.get(id=user_id)
            old_role = user_profile.role
            user_profile.role = new_role
            user_profile.save()
            messages.success(request, f'Role updated for {user_profile.user.email} from {old_role} to {new_role}')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User not found')
    
    users = UserProfile.objects.all().select_related('user').order_by('-created_at')
    return render(request, 'relationship_app/manage_roles.html', {'users': users})

@login_required
@user_passes_test(is_admin, login_url='/relationship/login/')
def user_management(request):
    """Admin view to manage all users"""
    users = CustomUser.objects.all().select_related('profile').order_by('-date_joined')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    # Filter by role
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    paginator = Paginator(users, 15)  # Show 15 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'relationship_app/user_management.html', {
        'page_obj': page_obj,
        'query': query,
        'role_filter': role_filter,
    })

# Book Management Views
@login_required
@permission_required('relationship_app.can_create', raise_exception=True)
def add_book(request):
    """View to add a new book (requires can_create permission)"""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('relationship_app:list_books')
        else:
            messages.error(request, 'Please correct the errors below.')
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
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('relationship_app:book_detail', pk=book.pk)
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
    books = Book.objects.all().select_related('author').order_by('title')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query)
        )
    
    paginator = Paginator(books, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'relationship_app/book_management.html', {
        'page_obj': page_obj,
        'query': query,
        'can_create': request.user.has_perm('relationship_app.can_create'),
        'can_delete': request.user.has_perm('relationship_app.can_delete')
    })

# Author Management Views
@login_required
@permission_required('relationship_app.can_create', raise_exception=True)
def add_author(request):
    """View to add a new author"""
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Author "{author.name}" added successfully!')
            return redirect('relationship_app:list_books')
    else:
        form = AuthorForm()
    
    return render(request, 'relationship_app/author_form.html', {
        'form': form,
        'title': 'Add New Author',
        'action': 'Add'
    })

# Library Management Views
@login_required
@permission_required('relationship_app.can_create_library', raise_exception=True)
def add_library(request):
    """View to add a new library (requires can_create_library permission)"""
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            library = form.save()
            messages.success(request, f'Library "{library.name}" created successfully!')
            return redirect('relationship_app:library_detail', pk=library.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LibraryForm()
    
    return render(request, 'relationship_app/library_form.html', {
        'form': form,
        'title': 'Add New Library',
        'action': 'Add'
    })

@login_required
@permission_required('relationship_app.can_edit_library', raise_exception=True)
def edit_library(request, pk):
    """View to edit a library (requires can_edit_library permission)"""
    library = get_object_or_404(Library, pk=pk)
    
    if request.method == 'POST':
        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            library = form.save()
            messages.success(request, f'Library "{library.name}" updated successfully!')
            return redirect('relationship_app:library_detail', pk=library.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LibraryForm(instance=library)
    
    return render(request, 'relationship_app/library_form.html', {
        'form': form,
        'title': 'Edit Library',
        'action': 'Update',
        'library': library
    })

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

# API Views for AJAX
@login_required
def get_user_stats(request):
    """API endpoint to get user statistics (for admin dashboard)"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    stats = {
        'total_users': CustomUser.objects.count(),
        'total_books': Book.objects.count(),
        'total_libraries': Library.objects.count(),
        'total_authors': Author.objects.count(),
        'users_by_role': {
            'admin': UserProfile.objects.filter(role='admin').count(),
            'librarian': UserProfile.objects.filter(role='librarian').count(),
            'member': UserProfile.objects.filter(role='member').count(),
        }
    }
    
    return JsonResponse(stats)