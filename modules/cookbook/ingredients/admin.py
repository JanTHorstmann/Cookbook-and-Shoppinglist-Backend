from django.contrib import admin
from .models import Ingredient

class IngredientAdmin(admin.ModelAdmin):
    fields = ["id","name"]

admin.site.register(Ingredient)