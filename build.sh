#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Checking Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"

echo "Checking database connection..."
python manage.py check --database default

echo "Showing migration status..."
python manage.py showmigrations

echo "Making migrations for all apps..."
python manage.py makemigrations

echo "Migrating inventory app first..."
python manage.py migrate inventory

echo "Migrating stock app..."
python manage.py migrate stock

echo "Running all remaining migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build completed successfully!"