from django.core.management.base import BaseCommand
from api.models import Book

class Command(BaseCommand):
    help = 'Seed the database with sample books'

    def handle(self, *args, **options):
        books = [
            {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald'},
            {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee'},
            {'title': '1984', 'author': 'George Orwell'},
            {'title': 'Pride and Prejudice', 'author': 'Jane Austen'},
            {'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger'},
        ]
        
        for book_data in books:
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                author=book_data['author']
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created book: {book.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Book already exists: {book.title}')
                )