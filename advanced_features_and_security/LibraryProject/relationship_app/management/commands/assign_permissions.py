from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from relationship_app.models import Book, UserProfile

class Command(BaseCommand):
    help = 'Assign permissions to users based on their roles'

    def handle(self, *args, **options):
        # Get permissions
        content_type = ContentType.objects.get_for_model(Book)
        
        can_add_book = Permission.objects.get(codename='can_add_book', content_type=content_type)
        can_change_book = Permission.objects.get(codename='can_change_book', content_type=content_type)
        can_delete_book = Permission.objects.get(codename='can_delete_book', content_type=content_type)
        
        # Assign permissions to admin users
        admin_users = UserProfile.objects.filter(role='admin')
        for profile in admin_users:
            user = profile.user
            user.user_permissions.add(can_add_book, can_change_book, can_delete_book)
            self.stdout.write(f'Added all book permissions to admin: {user.username}')
        
        # Assign permissions to librarian users
        librarian_users = UserProfile.objects.filter(role='librarian')
        for profile in librarian_users:
            user = profile.user
            user.user_permissions.add(can_add_book, can_change_book)
            self.stdout.write(f'Added add/change book permissions to librarian: {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Permissions assigned successfully!'))