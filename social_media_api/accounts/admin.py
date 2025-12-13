# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('bio', 'profile_picture', 'location', 'website', 'followers')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)