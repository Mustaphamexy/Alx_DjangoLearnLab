from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import CustomUser, UserProfile, Author, Book, Library, Librarian

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'date_of_birth', 'get_role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined', 'profile__role')
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
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'No role'
    get_role.short_description = 'Role'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at', 'updated_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'role')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'birth_date']
    list_filter = ['birth_date']
    search_fields = ['name', 'bio']
    fieldsets = (
        (None, {
            'fields': ('name', 'bio', 'birth_date')
        }),
    )

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'published_date']
    list_filter = ['author', 'published_date']
    search_fields = ['title', 'author__name', 'isbn']
    filter_horizontal = []
    
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'isbn')
        }),
        (_('Details'), {
            'fields': ('published_date', 'description', 'cover_image'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_book_count', 'created_at']
    list_filter = ['created_at']
    filter_horizontal = ['books']
    search_fields = ['name', 'address']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'address')
        }),
        (_('Books'), {
            'fields': ('books',),
            'classes': ('collapse',)
        }),
    )
    
    def get_book_count(self, obj):
        return obj.books.count()
    get_book_count.short_description = 'Number of Books'

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ['name', 'library', 'user_account']
    list_filter = ['library']
    search_fields = ['name', 'library__name', 'user_account__email']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'library', 'user_account')
        }),
    )

# Unregister default Group admin and register custom one if needed
admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_permission_count']
    filter_horizontal = ['permissions']
    
    def get_permission_count(self, obj):
        return obj.permissions.count()
    get_permission_count.short_description = 'Permissions Count'