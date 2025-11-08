from django.core.management.base import BaseCommand
from relationship_app.models import Author, Book, Library, Librarian

class Command(BaseCommand):
    help = 'Create sample data for relationship_app'

    def handle(self, *args, **options):
        # Create sample data (same as in query_samples.py)
        author1 = Author.objects.create(name="George Orwell")
        author2 = Author.objects.create(name="J.K. Rowling")
        author3 = Author.objects.create(name="J.R.R. Tolkien")
        
        book1 = Book.objects.create(title="1984", author=author1)
        book2 = Book.objects.create(title="Animal Farm", author=author1)
        book3 = Book.objects.create(title="Harry Potter and the Sorcerer's Stone", author=author2)
        book4 = Book.objects.create(title="The Hobbit", author=author3)
        book5 = Book.objects.create(title="The Lord of the Rings", author=author3)
        
        library1 = Library.objects.create(name="Central Library")
        library2 = Library.objects.create(name="City Public Library")
        
        library1.books.add(book1, book2, book3)
        library2.books.add(book3, book4, book5)
        
        Librarian.objects.create(name="Alice Johnson", library=library1)
        Librarian.objects.create(name="Bob Smith", library=library2)
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))