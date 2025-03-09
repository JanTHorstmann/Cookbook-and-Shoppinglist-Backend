from rest_framework import serializers
from .models import Ingredient

class IngredientSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingredient
        fields = ['id', 'name']

    def validate_name(self, value):
        return value.strip().lower() 
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)  # Standard-Daten abrufen
        representation['name'] = instance.name.capitalize()  # Name mit Großbuchstaben
        return representation