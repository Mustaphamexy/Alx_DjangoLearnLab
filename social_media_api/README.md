# Social Media API

A RESTful API for a social media platform built with Django and Django REST Framework.

## Features

- User Authentication (Registration, Login, Logout with Token-based authentication)
- User Profiles with bio, profile pictures, and follower system
- Posts and Comments functionality
- Follow/Unfollow system
- Notifications
- Likes on posts and comments

## Models
### CustomUser
Extends Django's AbstractUser with additional fields:

- bio - User biography

- profile_picture - Profile image

- location - User location

- website - Personal website

- followers - Many-to-many relationship for follow system


## Project Structure Files
Here's a summary of the files created:

social_media_api/settings.py - Django project settings

accounts/models.py - Custom user model

accounts/serializers.py - User serializers

accounts/views.py - Authentication views

accounts/urls.py - Account URLs

accounts/admin.py - Admin configuration

social_media_api/urls.py - Main project URLs

README.md - Project documentation