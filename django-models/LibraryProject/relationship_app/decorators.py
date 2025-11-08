from django.contrib.auth.decorators import user_passes_test, login_required
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def role_required(role_name):
    """
    Decorator for views that checks if the user has the specified role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('relationship_app:login')
            
            if hasattr(request.user, 'profile'):
                if request.user.profile.role == role_name:
                    return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return login_required(role_required('admin')(view_func))

def librarian_required(view_func):
    return login_required(role_required('librarian')(view_func))

def member_required(view_func):
    return login_required(role_required('member')(view_func))

# User test functions for user_passes_test decorator
def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

def is_librarian(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'librarian'

def is_member(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'member'