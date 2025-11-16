from django import forms
from .models import Book, Author

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']  # Add publication_year
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter book title',
                'style': 'width: 100%; padding: 8px; margin: 5px 0;'
            }),
            'author': forms.Select(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 8px; margin: 5px 0;'
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publication year',
                'style': 'width: 100%; padding: 8px; margin: 5px 0;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all().order_by('name')