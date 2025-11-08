## 1. Create Operation
```python
from bookshelf.models import Book
book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
```

## Output

<Book: 1984 by George Orwell (1949)>
Book ID: 1

## 2.Retrieve Operation

```python
from bookshelf.models import Book
book = Book.objects.get(title="1984")
print(f"Title: {book.title}")
print(f"Author: {book.author}") 
print(f"Publication Year: {book.publication_year}")
```

## Output 

Title: 1984
Author: George Orwell
Publication Year: 1949


## 3.Update Operation

```python
from bookshelf.models import Book
book = Book.objects.get(title="1984")
book.title = "Nineteen Eighty-Four"
book.save()
```

## Output 

'Nineteen Eighty-Four'
<Book: Nineteen Eighty-Four by George Orwell (1949)>

## 4.Delete Operation

```python 
from bookshelf.models import Book
book = Book.objects.get(title="Nineteen Eighty-Four")
book.delete()
all_books = Book.objects.all()
print(f"Total books: {all_books.count()}")
```

## Output 

Total books: 0
[]