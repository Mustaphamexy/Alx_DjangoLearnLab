
from bookshelf.models import Book
```python
# Retrieve and update the book
book = Book.objects.get(title="1984")
book.title = "Nineteen Eighty-Four"
book.save()
```

## Actual Command & Output:

```
>>> from bookshelf.models import Book
>>> book = Book.objects.get(title="1984")
>>> book.title = "Nineteen Eighty-Four"
>>> book.save()
>>> updated_book = Book.objects.get(id=book.id)
>>> updated_book.title
'Nineteen Eighty-Four'
>>> updated_book
<Book: Nineteen Eighty-Four by George Orwell (1949)>
```
