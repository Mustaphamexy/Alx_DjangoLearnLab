from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, Group
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

class CustomUserManager(BaseUserManager):
    """Custom user manager for handling user creation with additional fields"""
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """Custom user model with additional fields"""
    
    # Replace username with email as the primary identifier
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Additional custom fields
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    profile_photo = models.ImageField(
        _('profile photo'), 
        upload_to='profile_photos/',
        null=True, 
        blank=True
    )
    
    # Set email as the USERNAME_FIELD
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class Author(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    
    class Meta:
        permissions = [
            ("can_add_book", "Can add book"),
            ("can_change_book", "Can change book"),
            ("can_delete_book", "Can delete book"),
            # New custom permissions for this task
            ("can_view", "Can view books"),
            ("can_create", "Can create books"),
            ("can_edit", "Can edit books"),
            ("can_delete", "Can delete books"),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"

class Library(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book, related_name='libraries')
    
    class Meta:
        verbose_name_plural = "Libraries"
        # Add custom permissions for Library model
        permissions = [
            ("can_view_library", "Can view library"),
            ("can_create_library", "Can create library"),
            ("can_edit_library", "Can edit library"),
            ("can_delete_library", "Can delete library"),
        ]
    
    def __str__(self):
        return self.name

class Librarian(models.Model):
    name = models.CharField(max_length=100)
    library = models.OneToOneField(Library, on_delete=models.CASCADE, related_name='librarian')
    
    def __str__(self):
        return f"{self.name} - {self.library.name}"

# User Profile Model for Role-Based Access Control (now using CustomUser)
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    class Meta:
        permissions = [
            ("can_manage_roles", "Can manage user roles"),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"

# Signal to automatically create UserProfile when a new CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

# Signal to create default groups and permissions after migration
# Signal to create default groups and permissions after migration
@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Creates default groups with appropriate permissions after migrations.
    This ensures groups exist when the application is set up.
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    # Only run for relationship_app to avoid running multiple times
    if sender.name != 'relationship_app':
        return
    
    try:
        # Get content types specifically from relationship_app
        book_content_type = ContentType.objects.get(app_label='relationship_app', model='book')
        library_content_type = ContentType.objects.get(app_label='relationship_app', model='library')
    except ContentType.DoesNotExist:
        # If content types don't exist yet, skip group creation
        print("Content types not found - skipping group creation")
        return
    
    # Create or update Groups
    editors_group, created = Group.objects.get_or_create(name='Editors')
    viewers_group, created = Group.objects.get_or_create(name='Viewers')
    admins_group, created = Group.objects.get_or_create(name='Admins')
    
    # Clear existing permissions to avoid duplicates
    editors_group.permissions.clear()
    viewers_group.permissions.clear()
    admins_group.permissions.clear()
    
    # Assign permissions to Editors group (only from relationship_app)
    editor_perms = [
        'can_view', 'can_create', 'can_edit',
        'can_view_library', 'can_create_library', 'can_edit_library'
    ]
    
    for perm in editor_perms:
        try:
            # Use filter().first() to handle multiple permissions with same name
            permission = Permission.objects.filter(
                content_type__app_label='relationship_app', 
                codename=perm
            ).first()
            if permission:
                editors_group.permissions.add(permission)
        except Exception as e:
            print(f"Error adding permission {perm}: {e}")
    
    # Assign permissions to Viewers group (only from relationship_app)
    viewer_perms = ['can_view', 'can_view_library']
    for perm in viewer_perms:
        try:
            permission = Permission.objects.filter(
                content_type__app_label='relationship_app', 
                codename=perm
            ).first()
            if permission:
                viewers_group.permissions.add(permission)
        except Exception as e:
            print(f"Error adding permission {perm}: {e}")
    
    # Assign all permissions to Admins group
    all_perms = Permission.objects.all()
    admins_group.permissions.set(all_perms)
    
    print("Default groups created successfully!")