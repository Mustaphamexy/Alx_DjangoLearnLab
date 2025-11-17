# bookshelf/views.py - UPDATED
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.utils.html import escape
from django.http import JsonResponse
from .models import Book, Author
from .forms import BookForm, ExampleForm  # ADD ExampleForm import
import logging

# Security: Set up logger for security events
logger = logging.getLogger('django.security')

# ... (keep all existing functions)

# ADD THIS NEW FUNCTION
def example_form_view(request):
    """
    Example view demonstrating form usage
    """
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            logger.info(f"Form submitted by {name} ({email})")
            messages.success(request, 'Form submitted successfully!')
            return redirect('bookshelf:book_list')
    else:
        form = ExampleForm()
    
    return render(request, 'bookshelf/form_example.html', {
        'form': form,
        'title': 'Example Form',
        'action': 'Submit'
    })