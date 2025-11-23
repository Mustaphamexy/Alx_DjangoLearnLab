from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Create sample users with tokens for testing authentication'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created admin user: admin / admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )

        # Create regular user
        regular_user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@example.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            regular_user.set_password('user123')
            regular_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created regular user: user / user123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Regular user already exists')
            )

        # Create tokens for users
        admin_token, created = Token.objects.get_or_create(user=admin_user)
        user_token, created = Token.objects.get_or_create(user=regular_user)

        self.stdout.write(
            self.style.SUCCESS(f'Admin token: {admin_token.key}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'User token: {user_token.key}')
        )
        self.stdout.write(
            self.style.SUCCESS('Sample users and tokens created successfully!')
        )