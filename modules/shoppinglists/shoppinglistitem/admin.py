from django.contrib import admin
from .models import ShoppingListItem

class ShoppingListItemAdmin(admin.ModelAdmin):
    fields = ["id", "ingredient", "amount", "unit"]

admin.site.register(ShoppingListItem)
