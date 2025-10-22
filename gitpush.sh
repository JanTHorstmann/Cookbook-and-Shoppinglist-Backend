if [ -z "$1" ]; then
  echo "⚠️  Bitte eine Commit-Nachricht angeben!"
  echo "➡️  Beispiel: ./gitpush.sh 'Update README'"
  exit 1
fi

# Änderungen hinzufügen
git add .

# Commit mit übergebener Nachricht
git commit -m "$1"

# Push zum Remote-Repository
git push

echo "✅ Änderungen erfolgreich gepusht!"
