from rest_framework import serializers
from .models import RecipeIngredient
from modules.cookbook.ingredients.models import Ingredient 

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = ["id", "ingredient", "amount", "unit"]

    def create(self, validated_data):
        ingredient_name = validated_data["ingredient"].strip().lower()
        ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
        return RecipeIngredient.objects.create(ingredient=ingredient, amount=validated_data["amount"], unit=validated_data["unit"])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["ingredient"] = instance.ingredient.name.capitalize()
        return representation