from rest_framework import serializers
from .models import ListCollection

class ListCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListCollection
        fields = ["id", "name", "participants", "author"]