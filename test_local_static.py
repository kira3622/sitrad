import requests
import os

# Test local static files
base_url = 'http://127.0.0.1:8000'
static_files = [
    '/static/css/material_dashboard.css',
    '/static/css/sitrad_modern.css', 
    '/static/js/material_dashboard.js'
]

print('Testing local static files:')
for file_path in static_files:
    try:
        response = requests.head(f'{base_url}{file_path}', timeout=5)
        status = "OK" if response.status_code == 200 else "ERROR"
        print(f'{file_path}: {response.status_code} ({status})')
    except Exception as e:
        print(f'{file_path}: ERROR - {e}')