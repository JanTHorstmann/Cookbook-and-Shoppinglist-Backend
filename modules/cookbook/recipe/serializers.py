from rest_framework import serializers
from .models import Recipe, RecipeIngredient

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.StringRelatedField()  # Gibt den Namen der Zutat aus

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "amount"]
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source="recipeingredient_set", many=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Recipe
        fields = ["id", "name", "instructions", "preparation_time", "difficulty", "author", "ingredients"]

    def validate_name(self, value):
        return value.strip().lower() 
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)  # Standard-Daten abrufen
        representation['name'] = instance.name.capitalize()  # Name mit Großbuchstaben
        return representation