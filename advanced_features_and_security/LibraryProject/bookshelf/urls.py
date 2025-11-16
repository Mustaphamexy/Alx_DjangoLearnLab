from django.urls import path
from . import views

app_name = 'bookshelf'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('add/', views.book_add, name='book_add'),
    path('<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('api/search/', views.safe_search_api, name='safe_search_api'),
]