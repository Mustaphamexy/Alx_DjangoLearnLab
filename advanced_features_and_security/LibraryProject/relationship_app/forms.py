from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, Book, Author, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Format: YYYY-MM-DD"
    )
    role = forms.ChoiceField(
        choices=[
            ('admin', 'Admin'),
            ('librarian', 'Librarian'), 
            ('member', 'Member')
        ],
        initial='member',
        required=True,
        help_text="Select your role in the system"
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'date_of_birth', 'profile_photo', 'password1', 'password2', 'role')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Set the role in the user profile
            user.profile.role = self.cleaned_data['role']
            user.profile.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """Form for updating users with custom fields"""
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'date_of_birth', 'profile_photo')

class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form that uses email instead of username"""
    username = forms.EmailField(label='Email')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all().order_by('name')