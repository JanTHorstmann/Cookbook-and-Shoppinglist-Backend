from django.contrib import admin
from .models import RecipeIngredient

class RecipeAdmin(admin.ModelAdmin):
    fields = ["id", "ingredient", "amount", "unit"]

admin.site.register(RecipeIngredient)
