from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
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
        
        # Create user profile
        UserProfile.objects.create(user=user)
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

        user = self.create_user(email, password, **extra_fields)
        
        # Set admin role for superuser
        user_profile = UserProfile.objects.get(user=user)
        user_profile.role = 'admin'
        user_profile.save()
        
        return user

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
        permissions = [
            ("can_view", "Can view books"),
            ("can_add_book", "Can add books"),
            ("can_create", "Can create content"),
            ("can_edit", "Can edit content"),
            ("can_delete", "Can delete content"),
            ("can_view_library", "Can view libraries"),
            ("can_create_library", "Can create libraries"),
            ("can_edit_library", "Can edit libraries"),
            ("can_delete_library", "Can delete libraries"),
        ]

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='member'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.role}"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.get_or_create(user=instance)

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author, 
        on_delete=models.CASCADE, 
        related_name='books'
    )
    isbn = models.CharField(max_length=13, unique=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(
        upload_to='book_covers/', 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"
    
    class Meta:
        ordering = ['title']

class Library(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    books = models.ManyToManyField(Book, related_name='libraries', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Libraries"
        ordering = ['name']

class Librarian(models.Model):
    name = models.CharField(max_length=100)
    library = models.ForeignKey(
        Library, 
        on_delete=models.CASCADE, 
        related_name='librarians'
    )
    user_account = models.OneToOneField(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='librarian_profile'
    )
    
    def __str__(self):
        return f"{self.name} - {self.library.name}"

# Signal to set up default permissions and groups
@receiver(post_save, sender=ContentType)
def setup_default_permissions(sender, instance, **kwargs):
    """Create default groups and permissions if they don't exist"""
    if instance.app_label == 'relationship_app':
        # Create default groups
        admin_group, created = Group.objects.get_or_create(name='Admins')
        librarian_group, created = Group.objects.get_or_create(name='Librarians') 
        member_group, created = Group.objects.get_or_create(name='Members')
        
        # Get all permissions for this app
        permissions = Permission.objects.filter(content_type=instance)
        
        # Assign permissions to groups
        if instance.model == 'customuser':
            # Admins get all permissions
            for perm in permissions:
                admin_group.permissions.add(perm)
            
            # Librarians get specific permissions
            librarian_perms = permissions.filter(
                codename__in=['can_view', 'can_add_book', 'can_create', 'can_edit', 'can_view_library']
            )
            for perm in librarian_perms:
                librarian_group.permissions.add(perm)
            
            # Members get basic permissions
            member_perms = permissions.filter(
                codename__in=['can_view', 'can_view_library']
            )
            for perm in member_perms:
                member_group.permissions.add(perm)