 ```python
from bookshelf.models import Book

# Delete the book
book = Book.objects.get(title="Nineteen Eighty-Four")
book.delete()

# Verify deletion
all_books = Book.objects.all()
print(f"Total books in database: {all_books.count()}")
```

## Actual Command & Output:

```
>>> from bookshelf.models import Book
>>> book = Book.objects.get(title="Nineteen Eighty-Four")
>>> book.delete()
(1, {'bookshelf.Book': 1})
>>> all_books = Book.objects.all()
>>> print(f"Total books in database: {all_books.count()}")
Total books in database: 0
>>> list(all_books)
[]
```