from django.contrib import admin
from .models import Favorite

class FavoritesAdmin(admin.ModelAdmin):
    fields = ["id", "user", "recipe", "created_at"]

admin.site.register(Favorite)
