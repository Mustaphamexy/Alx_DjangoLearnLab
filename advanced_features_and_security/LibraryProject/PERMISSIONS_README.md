# Permissions and Groups Setup Guide

## Overview
This Django application implements a comprehensive permissions and groups system to control access to various parts of the application.

## Custom Permissions Defined

### Book Model Permissions
- `can_view` - View books
- `can_create` - Create new books  
- `can_edit` - Edit existing books
- `can_delete` - Delete books

### Library Model Permissions
- `can_view_library` - View libraries
- `can_create_library` - Create new libraries
- `can_edit_library` - Edit existing libraries
- `can_delete_library` - Delete libraries

## Default Groups

### 1. Viewers Group
- Permissions: `can_view`, `can_view_library`
- Can only view books and libraries, no editing capabilities

### 2. Editors Group  
- Permissions: `can_view`, `can_create`, `can_edit`, `can_view_library`, `can_create_library`, `can_edit_library`
- Can view, create, and edit books and libraries, but cannot delete

### 3. Admins Group
- Permissions: All permissions
- Full access to all features including deletion

## How to Test

### Setup Test Users
1. Create test users in Django admin
2. Assign them to different groups
3. Test access to various features

### Expected Behavior
- **Viewers**: Can only see book/list and library/list pages
- **Editors**: Can create/edit books and libraries but not delete
- **Admins**: Full access to all features

### Manual Testing Steps
1. Log in as a Viewer - verify limited access
2. Log in as an Editor - verify create/edit capabilities  
3. Log in as an Admin - verify full access
4. Test permission-denied responses for unauthorized actions

## Code Implementation

### Permission Checks in Views
- Used `@permission_required` decorator for function-based views
- Used `dispatch()` method override for class-based views
- Manual permission checks with `request.user.has_perm()`

### Automatic Group Creation
Groups are automatically created via Django signals after migrations run.