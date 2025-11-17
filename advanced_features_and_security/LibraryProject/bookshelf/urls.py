# bookshelf/urls.py - UPDATED
from django.urls import path
from . import views

app_name = 'bookshelf'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('example-form/', views.example_form_view, name='example_form'),  # ADD THIS
    path('api/search/', views.safe_search_api, name='safe_search_api'),
]