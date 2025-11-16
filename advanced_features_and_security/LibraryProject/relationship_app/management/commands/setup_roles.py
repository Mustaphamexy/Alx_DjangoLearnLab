from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from relationship_app.models import UserProfile

class Command(BaseCommand):
    help = 'Setup users with different roles for testing'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@library.com'}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_user.profile.role = 'admin'
            admin_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create librarian user
        librarian_user, created = User.objects.get_or_create(
            username='librarian',
            defaults={'email': 'librarian@library.com'}
        )
        if created:
            librarian_user.set_password('librarian123')
            librarian_user.save()
            librarian_user.profile.role = 'librarian'
            librarian_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created librarian user'))

        # Create member user
        member_user, created = User.objects.get_or_create(
            username='member',
            defaults={'email': 'member@library.com'}
        )
        if created:
            member_user.set_password('member123')
            member_user.save()
            member_user.profile.role = 'member'
            member_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created member user'))

        self.stdout.write(self.style.SUCCESS('All test users created successfully!'))
        self.stdout.write('Admin: username=admin, password=admin123')
        self.stdout.write('Librarian: username=librarian, password=librarian123')
        self.stdout.write('Member: username=member, password=member123')