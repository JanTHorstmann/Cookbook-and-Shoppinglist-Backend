from django.contrib import admin
from .models import ListCollection

class ListCollectionAdmin(admin.ModelAdmin):
    fields = ["id", "name", "participants", "author"]

admin.site.register(ListCollection)
