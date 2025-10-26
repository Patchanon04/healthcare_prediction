#!/bin/bash
# Generate and run migrations for treatment management models

echo "🔄 Making migrations..."
python manage.py makemigrations predictions

echo "🚀 Running migrations..."
python manage.py migrate

echo "✅ Migrations complete!"
