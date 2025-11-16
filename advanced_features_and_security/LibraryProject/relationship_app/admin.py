from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile, Author, Book, Library, Librarian

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'date_of_birth', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 
                'last_name', 
                'date_of_birth', 
                'profile_photo'
            )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'last_name',
                'date_of_birth',
                'profile_photo',
                'password1', 
                'password2',
                'is_staff', 
                'is_active'
            ),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']
    list_filter = ['author']
    search_fields = ['title', 'author__name']

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['books']  # Better UI for ManyToMany
    search_fields = ['name']

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ['name', 'library']
    list_filter = ['library']
    search_fields = ['name', 'library__name']