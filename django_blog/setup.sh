#!/bin/bash
# setup.sh - Setup script for Django Blog Project

echo "Setting up Django Blog Project..."

# Create virtual environment (optional)
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Django
echo "Installing Django..."
pip install django

# Make migrations
echo "Making migrations..."
python manage.py makemigrations blog
python manage.py migrate

# Create superuser (optional)
echo "Creating superuser..."
python manage.py createsuperuser

echo "Setup complete!"
echo "To run the server: python manage.py runserver"