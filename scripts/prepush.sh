#!/bin/bash
# ===========================
# Pre-push script for Django
# ===========================

echo "🔍 Running tests before pushing..."

# Führe Django Tests aus
python manage.py test

# Statuscode abfragen
if [ $? -eq 0 ]; then
    echo "✅ All tests passed. Proceeding with git push..."
    git push
else
    echo "❌ Tests failed! Commit NOT pushed."
    exit 1
fi