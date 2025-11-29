# API Query Examples - Filtering, Searching, and Ordering

## Base URL
All examples use the base URL: `http://localhost:8000/api/`

## Filtering Examples

### Exact Match Filtering
```http
GET /api/books/?title=1984
GET /api/books/?author=1
GET /api/books/?publication_year=1997 
```
## Partial Match Filtering
``` http
GET /api/books/?title_icontains=harry
GET /api/books/?author_name=rowling
```
## Range Filtering
``` http
GET /api/books/?publication_year_min=1900&publication_year_max=2000
GET /api/books/?created_after=2023-01-01T00:00:00Z
```
## Search Examples
### Basic Search
``` http
GET /api/books/?search=potter
GET /api/books/?search=orwell
```
## Dedicated Search Endpoint
```http
GET /api/books/search/?search=python
```
## Ordering Examples
### Single Field Ordering
``` http
GET /api/books/?ordering=title         
GET /api/books/?ordering=-publication_year 
```
## Multiple Field Ordering
```http
GET /api/books/?ordering=author__name,title
```
# Filter, search, and order together
```GET /api/books/?author_name=rowling&search=harry&ordering=-publication_year```

# Complex range filtering with ordering
``` GET /api/books/?publication_year_min=1900&publication_year_max=2000&ordering=title```
Available Filters
Book Filters
title: Exact title match

title_icontains: Partial title match (case-insensitive)

author: Author ID

author_name: Partial author name match

publication_year: Exact year

publication_year_min: Minimum year

publication_year_max: Maximum year

created_after: Books created after date

created_before: Books created before date

Search Fields
title

author__name

Ordering Fields
title

publication_year

created_at

updated_at

author__name

text

## Run and Test Your Implementation

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test api.tests.FilterSearchOrderTests

# Start server and test manually
python manage.py runserver
Now you can test your enhanced API with queries like:

http://localhost:8000/api/books/?author=1

http://localhost:8000/api/books/?search=harry&ordering=-publication_year

http://localhost:8000/api/books/?publication_year_min=1900&publication_year_max=2000

```