from django.contrib import admin
from .models import ShoppingListItem

class ShoppingListItemAdmin(admin.ModelAdmin):
    fields = ["id", "ingredient", "amount", "unit", "shopping_list"]
    list_display = ["id", "ingredient", "amount", "unit", "shopping_list"]

admin.site.register(ShoppingListItem)
