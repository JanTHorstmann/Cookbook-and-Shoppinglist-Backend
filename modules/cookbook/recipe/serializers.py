from rest_framework import serializers
from .models import Recipe, RecipeIngredient
from modules.cookbook.ingredients.models import Ingredient 

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())  
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "ingredient_name", "amount"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["ingredient_name"] = instance.ingredient.name.capitalize()  # Name mit Großbuchstaben
        return representation
    

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