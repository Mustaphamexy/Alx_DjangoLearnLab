from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Post, Comment, Category, Tag
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'your.email@example.com',
        'class': 'form-control'
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'First Name',
        'class': 'form-control'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Last Name',
        'class': 'form-control'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a username',
                'class': 'form-control'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Create a strong password',
                'class': 'form-control'
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirm your password',
                'class': 'form-control'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already in use.')
        return email

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'profile_picture', 'website', 'github', 'twitter']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Tell us about yourself...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourwebsite.com'}),
            'github': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/username'}),
        }

class TagWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            if isinstance(value, str):
                tags = value.split(',')
            elif hasattr(value, 'all'):
                tags = [tag.name for tag in value.all()]
            else:
                tags = value
            value = ', '.join([tag.strip() for tag in tags if tag.strip()])
        return super().render(name, value, attrs, renderer)

class PostForm(forms.ModelForm):
    """Form for creating and updating blog posts"""
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'category-checkbox'}),
        required=False
    )
    
    tags_input = forms.CharField(
        required=False,
        widget=TagWidget(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas',
            'data-role': 'tagsinput'
        }),
        help_text="Separate tags with commas"
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'excerpt', 'status', 'categories', 'tags_input', 'featured_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a compelling title for your post'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your amazing content here...',
                'id': 'post-content'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary of your post (optional)'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            tags = self.instance.tags.all()
            if tags:
                self.initial['tags_input'] = ', '.join([tag.name for tag in tags])
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError("Title must be at least 10 characters long.")
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 50:
            raise ValidationError("Content must be at least 50 characters long.")
        return content
    
    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '')
        if tags_input:
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            if len(tags) > 10:
                raise ValidationError("Maximum 10 tags allowed.")
            for tag in tags:
                if len(tag) > 50:
                    raise ValidationError(f"Tag '{tag}' is too long (max 50 characters).")
        return tags_input
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
        
        # Handle tags
        tags_input = self.cleaned_data.get('tags_input', '')
        if tags_input:
            tags = []
            for tag_name in [tag.strip() for tag in tags_input.split(',') if tag.strip()]:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': slugify(tag_name)}
                )
                tags.append(tag)
            instance.tags.set(tags)
        
        # Save many-to-many relationships
        if commit:
            self.save_m2m()
        
        return instance

class CommentForm(forms.ModelForm):
    """Form for adding comments to posts"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts...',
                'id': 'comment-content'
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        if len(content.strip()) > 1000:
            raise ValidationError("Comment must be less than 1000 characters.")
        return content

class CommentUpdateForm(forms.ModelForm):
    """Form for updating comments"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Edit your comment...',
                'id': 'comment-content-edit'
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        if len(content.strip()) > 1000:
            raise ValidationError("Comment must be less than 1000 characters.")
        return content

# FIXED: Added CommentDeleteForm
class CommentDeleteForm(forms.Form):
    """Form for confirming comment deletion"""
    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True
    )

class AdvancedSearchForm(forms.Form):
    """Form for advanced search functionality"""
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...',
            'aria-label': 'Search'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    author = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    STATUS_CHOICES = [
        ('', 'All Status'),
        ('published', 'Published'),
        ('draft', 'Draft'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class SearchForm(forms.Form):
    """Simple search form for the navbar"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...',
            'aria-label': 'Search'
        })
    )

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})