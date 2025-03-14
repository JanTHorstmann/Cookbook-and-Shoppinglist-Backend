from django.contrib import admin
from .models import Recipe

class RecipeAdmin(admin.ModelAdmin):
    fields = ["id", "name", "instructions", "preparation_time", "difficulty", "author", "ingredients"]

admin.site.register(Recipe)
